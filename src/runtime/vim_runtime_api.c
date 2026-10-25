/* vi:set ts=8 sts=4 sw=4 noet:
 *
 * A minimal same-DLL, two-handle runtime entry for Windows.  Each VimMain
 * invocation keeps its whole C call stack on one _beginthreadex owner thread.
 */

#include "vim_runtime_api.h"

#ifdef VIM_RUNTIME_LIBRARY

#include <windows.h>
#include <process.h>
#include <setjmp.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

extern int VimMain(int argc, char **argv);

struct vim_runtime_instance
{
    HANDLE thread;
    unsigned thread_id;
    int argc;
    char **argv;
    char **owned_argv;
    int exit_status;
    HWND window;
    HWND parent_window;
    volatile LONG gui_ready;
    unsigned long long serial;
};

static volatile LONG64 next_instance_serial;
static __declspec(thread) jmp_buf *exit_landing;
static __declspec(thread) int worker_exit_status;
static __declspec(thread) vim_runtime_instance *current_runtime_instance;

typedef struct
{
    HWND window;
    unsigned thread_id;
} runtime_window_search;

    static BOOL CALLBACK
find_vim_window(HWND window, LPARAM opaque)
{
    runtime_window_search *search = (runtime_window_search *)opaque;
    WCHAR class_name[32];

    if (GetWindowThreadProcessId(window, NULL) == search->thread_id
	&& GetClassNameW(window, class_name, 32) != 0
	&& wcscmp(class_name, L"Vim") == 0)
    {
	search->window = window;
	return FALSE;
    }
    return TRUE;
}

    static void
free_instance(vim_runtime_instance *instance)
{
    int i;

    if (instance == NULL)
	return;
    if (instance->argv != NULL)
    {
	for (i = 0; i < instance->argc; ++i)
	    free(instance->owned_argv[i]);
	free(instance->argv);
    }
    free(instance);
}

    static unsigned __stdcall
instance_thread(void *opaque)
{
    vim_runtime_instance *instance = (vim_runtime_instance *)opaque;
    jmp_buf landing;

    current_runtime_instance = instance;
    exit_landing = &landing;
    if (setjmp(landing) == 0)
	instance->exit_status = VimMain(instance->argc, instance->argv);
    else
	instance->exit_status = worker_exit_status;
    vim_runtime_console_cleanup();
    exit_landing = NULL;
    current_runtime_instance = NULL;
    return (unsigned)instance->exit_status;
}

    vim_runtime_instance *VIM_RUNTIME_CALL
vim_runtime_instance_create(int argc, const char *const *argv)
{
    vim_runtime_instance *instance;
    int i;
    uintptr_t thread;

    if (argc < 1 || argv == NULL || argv[0] == NULL || argv[0][0] == '\0'
	|| (size_t)argc >= ((size_t)-1 / sizeof(char *) / 2) - 1)
    {
	SetLastError(ERROR_INVALID_PARAMETER);
	return NULL;
    }

    instance = (vim_runtime_instance *)calloc(1, sizeof(*instance));
    if (instance == NULL)
    {
	SetLastError(ERROR_OUTOFMEMORY);
	return NULL;
    }
    instance->argc = argc;
    instance->serial = (unsigned long long)InterlockedIncrement64(
						    &next_instance_serial);
    instance->argv = (char **)calloc(((size_t)argc + 1) * 2, sizeof(char *));
    if (instance->argv == NULL)
    {
	free_instance(instance);
	SetLastError(ERROR_OUTOFMEMORY);
	return NULL;
    }
    // Vim's startup parser may move/remove argv entries.  Retain the original
    // pointers in a separate half of the allocation for exactly-once cleanup.
    instance->owned_argv = instance->argv + argc + 1;
    for (i = 0; i < argc; ++i)
    {
	size_t len;

	if (argv[i] == NULL)
	{
	    free_instance(instance);
	    SetLastError(ERROR_INVALID_PARAMETER);
	    return NULL;
	}
	len = strlen(argv[i]) + 1;
	instance->argv[i] = (char *)malloc(len);
	instance->owned_argv[i] = instance->argv[i];
	if (instance->argv[i] == NULL)
	{
	    free_instance(instance);
	    SetLastError(ERROR_OUTOFMEMORY);
	    return NULL;
	}
	memcpy(instance->argv[i], argv[i], len);
    }
    for (i = 1; i + 1 < argc; ++i)
    {
	if (strcmp(instance->argv[i], "--windowid") == 0)
	{
	    char *end;
	    unsigned __int64 id = _strtoui64(instance->argv[i + 1], &end, 0);

	    if (end != instance->argv[i + 1] && *end == '\0')
		instance->parent_window = (HWND)(uintptr_t)id;
	    ++i;
	}
    }

    // Match the standalone target's 8 MiB reserve, independent of the host
    // executable's default stack.  Pages are committed on demand by Windows.
    thread = _beginthreadex(NULL, 8 * 1024 * 1024, instance_thread, instance,
				STACK_SIZE_PARAM_IS_A_RESERVATION,
						    &instance->thread_id);
    if (thread == 0)
    {
	free_instance(instance);
	return NULL;
    }
    instance->thread = (HANDLE)thread;
    return instance;
}

    int VIM_RUNTIME_CALL
vim_runtime_instance_wait(vim_runtime_instance *instance,
				 unsigned long timeout_ms, int *exit_status)
{
    DWORD result;

    if (instance == NULL || GetCurrentThreadId() == instance->thread_id)
    {
	SetLastError(ERROR_INVALID_PARAMETER);
	return -1;
    }
    result = WaitForSingleObject(instance->thread, (DWORD)timeout_ms);
    if (result == WAIT_TIMEOUT)
	return 0;
    if (result != WAIT_OBJECT_0)
	return -1;
    if (exit_status != NULL)
	*exit_status = instance->exit_status;
    return 1;
}

    int VIM_RUNTIME_CALL
vim_runtime_instance_destroy(vim_runtime_instance *instance)
{
    DWORD result;

    if (instance == NULL)
    {
	SetLastError(ERROR_INVALID_PARAMETER);
	return -1;
    }
    result = WaitForSingleObject(instance->thread, 0);
    if (result == WAIT_TIMEOUT)
	return 0;
    if (result != WAIT_OBJECT_0)
	return -1;
    CloseHandle(instance->thread);
    free_instance(instance);
    return 1;
}

    void *VIM_RUNTIME_CALL
vim_runtime_instance_window(vim_runtime_instance *instance)
{
    runtime_window_search search = {NULL, 0};

    if (instance == NULL)
    {
	SetLastError(ERROR_INVALID_PARAMETER);
	return NULL;
    }
    if (WaitForSingleObject(instance->thread, 0) != WAIT_TIMEOUT)
	return NULL;
    if (InterlockedCompareExchange(&instance->gui_ready, 0, 0) == 0)
	return NULL;
    if (instance->window != NULL
	&& GetWindowThreadProcessId(instance->window, NULL) == instance->thread_id)
	return (void *)instance->window;
    search.thread_id = instance->thread_id;
    if (instance->parent_window != NULL && IsWindow(instance->parent_window))
	EnumChildWindows(instance->parent_window, find_vim_window,
							    (LPARAM)&search);
	if (search.window == NULL)
	EnumThreadWindows(instance->thread_id, find_vim_window, (LPARAM)&search);
    instance->window = search.window;
    return (void *)instance->window;
}

    int VIM_RUNTIME_CALL
vim_runtime_instance_request_close(vim_runtime_instance *instance)
{
    HWND window = (HWND)vim_runtime_instance_window(instance);

    if (window == NULL)
	return instance == NULL ? -1 : 0;
    if (!PostMessageW(window, WM_CLOSE, 0, 0))
	return -1;
    return 1;
}

    void
vim_runtime_thread_exit(int exit_status)
{
    worker_exit_status = exit_status;
    if (exit_landing != NULL)
	longjmp(*exit_landing, 1);

    /* A traditional VIMDLL launcher still calls VimMain directly. */
    exit(exit_status);
}

    void
vim_runtime_thread_gui_ready(void)
{
    if (current_runtime_instance != NULL)
	InterlockedExchange(&current_runtime_instance->gui_ready, 1);
}

    unsigned long long
vim_runtime_thread_serial(void)
{
    return current_runtime_instance == NULL ? 0
					: current_runtime_instance->serial;
}

#endif /* VIM_RUNTIME_LIBRARY */
