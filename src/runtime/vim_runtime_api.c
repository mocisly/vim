/* vi:set ts=8 sts=4 sw=4 noet:
 *
 * A minimal same-DLL, two-handle runtime entry for Windows.  Each VimMain
 * invocation keeps its whole C call stack on one _beginthreadex owner thread.
 */

#include "vim_runtime_api.h"

#ifdef VIM_RUNTIME_LIBRARY

#include "vim.h"

#include <windows.h>
#include <process.h>
#include <setjmp.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

extern int vim_runtime_handle_drop_one(char_u *path, void (*callback)(void *), void *cookie);

extern int VimMain(int argc, char **argv);

typedef struct vim_runtime_open_request
{
    struct vim_runtime_open_request *next;
    vim_runtime_instance *owner;
    wchar_t *path;
} vim_runtime_open_request;

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
    CRITICAL_SECTION open_lock;
    int open_lock_ready;
    volatile LONG stopping;
    vim_runtime_open_request *open_head;
    vim_runtime_open_request *open_tail;
    vim_runtime_open_request *open_active;
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
free_open_request(vim_runtime_open_request *request)
{
    if (request != NULL)
    {
        free(request->path);
        free(request);
    }
}

    static void
free_instance(vim_runtime_instance *instance)
{
    int i;

    vim_runtime_open_request *request;

    if (instance == NULL)
        return;
    request = instance->open_head;
    while (request != NULL)
    {
        vim_runtime_open_request *next = request->next;
        free_open_request(request);
        request = next;
    }
    free_open_request(instance->open_active);
    if (instance->open_lock_ready)
        DeleteCriticalSection(&instance->open_lock);
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
    InterlockedExchange(&instance->stopping, 1);
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
    if (!InitializeCriticalSectionEx(&instance->open_lock, 0, 0))
    {
        free_instance(instance);
        SetLastError(ERROR_OUTOFMEMORY);
        return NULL;
    }
    instance->open_lock_ready = 1;
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

    int VIM_RUNTIME_CALL
vim_runtime_instance_open_file_w(vim_runtime_instance *instance,
                                 const wchar_t *absolute_path)
{
    vim_runtime_open_request *request;
    vim_runtime_open_request *old_tail;
    HWND window;
    size_t length;

    if (instance == NULL || absolute_path == NULL || absolute_path[0] == L'\0')
    {
        SetLastError(ERROR_INVALID_PARAMETER);
        return -1;
    }
    length = wcslen(absolute_path);
    if (length >= 32767)
    {
        SetLastError(ERROR_FILENAME_EXCED_RANGE);
        return -1;
    }
    if (WaitForSingleObject(instance->thread, 0) != WAIT_TIMEOUT
            || InterlockedCompareExchange(&instance->stopping, 0, 0) != 0)
    {
        SetLastError(ERROR_INVALID_HANDLE);
        return -1;
    }
    window = (HWND)vim_runtime_instance_window(instance);
    if (window == NULL)
        return WaitForSingleObject(instance->thread, 0) == WAIT_TIMEOUT ? 0 : -1;

    request = (vim_runtime_open_request *)calloc(1, sizeof(*request));
    if (request == NULL)
    {
        SetLastError(ERROR_OUTOFMEMORY);
        return -1;
    }
    request->path = (wchar_t *)malloc((length + 1) * sizeof(wchar_t));
    if (request->path == NULL)
    {
        free_open_request(request);
        SetLastError(ERROR_OUTOFMEMORY);
        return -1;
    }
    memcpy(request->path, absolute_path, (length + 1) * sizeof(wchar_t));
    request->owner = instance;

    EnterCriticalSection(&instance->open_lock);
    if (InterlockedCompareExchange(&instance->stopping, 0, 0) != 0
            || WaitForSingleObject(instance->thread, 0) != WAIT_TIMEOUT)
    {
        LeaveCriticalSection(&instance->open_lock);
        free_open_request(request);
        SetLastError(ERROR_INVALID_HANDLE);
        return -1;
    }
    old_tail = instance->open_tail;
    if (old_tail != NULL)
        old_tail->next = request;
    else
        instance->open_head = request;
    instance->open_tail = request;
    if (!PostMessageW(window, WM_NULL, 0, 0))
    {
        if (old_tail != NULL)
            old_tail->next = NULL;
        else
            instance->open_head = NULL;
        instance->open_tail = old_tail;
        LeaveCriticalSection(&instance->open_lock);
        free_open_request(request);
        return -1;
    }
    LeaveCriticalSection(&instance->open_lock);
    return 1;
}

    void
vim_runtime_thread_open_done(void *cookie)
{
    vim_runtime_open_request *request = (vim_runtime_open_request *)cookie;
    vim_runtime_instance *instance = request->owner;
    HWND window;

    EnterCriticalSection(&instance->open_lock);
    if (instance->open_active == request)
        instance->open_active = NULL;
    window = instance->window;
    LeaveCriticalSection(&instance->open_lock);
    free_open_request(request);
    if (window != NULL)
        PostMessageW(window, WM_NULL, 0, 0);
}

    void
vim_runtime_thread_process_open_files(void)
{
    vim_runtime_instance *instance = current_runtime_instance;
    vim_runtime_open_request *request;
    char_u *path;
    int result;

    if (instance == NULL || InterlockedCompareExchange(&instance->gui_ready, 0, 0) == 0)
        return;
    EnterCriticalSection(&instance->open_lock);
    request = instance->open_active == NULL ? instance->open_head : NULL;
    if (request != NULL)
    {
        instance->open_head = request->next;
        if (instance->open_head == NULL)
            instance->open_tail = NULL;
        request->next = NULL;
        instance->open_active = request;
    }
    LeaveCriticalSection(&instance->open_lock);
    if (request == NULL)
        return;

    path = utf16_to_enc(request->path, NULL);
    if (path == NULL || *path == NUL)
    {
        vim_free(path);
        emsg("Vim runtime could not convert the requested file path");
        vim_runtime_thread_open_done(request);
        return;
    }
    result = vim_runtime_handle_drop_one(path, vim_runtime_thread_open_done,
                                          request);
    if (result == 1)
        return; // handle_drop owns path and will invoke the completion callback.
    vim_free(path);

    EnterCriticalSection(&instance->open_lock);
    instance->open_active = NULL;
    if (result == 0)
    {
        request->next = instance->open_head;
        instance->open_head = request;
        if (instance->open_tail == NULL)
            instance->open_tail = request;
    }
    LeaveCriticalSection(&instance->open_lock);
    if (result < 0)
    {
        emsg("Vim runtime could not queue the requested file");
        free_open_request(request);
    }
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
