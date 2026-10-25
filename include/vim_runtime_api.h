/* vi:set ts=8 sts=4 sw=4 noet:
 *
 * Windows runtime-library entry point for independent Vim threads.
 * The caller supplies writable-by-copy command-line arguments.
 * See docs/dual-instance-runtime.md for the instance/process ownership boundary.
 * Serialize all calls on a given handle. Different handles may run concurrently.
 * Keep this DLL loaded until all workers have exited and handles are destroyed.
 */

#ifndef VIM_RUNTIME_API_H
#define VIM_RUNTIME_API_H

#include <wchar.h>

#define VIM_RUNTIME_API_VERSION 2

#if defined(_WIN32)
# if defined(VIM_RUNTIME_LIBRARY)
#  define VIM_RUNTIME_API __declspec(dllexport)
# else
#  define VIM_RUNTIME_API __declspec(dllimport)
# endif
# define VIM_RUNTIME_CALL __cdecl
#else
# define VIM_RUNTIME_API
# define VIM_RUNTIME_CALL
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct vim_runtime_instance vim_runtime_instance;

#define VIM_RUNTIME_WAIT_FOREVER 0xffffffffUL

/* Start VimMain on a dedicated CRT thread.  argv[0] must be nonempty.
 * Arguments are copied before this function returns.  Returns NULL on error.
 * Ex and native Win32 GUI sessions are exercised by the current probes.
 * The caller must keep using wait/destroy until the worker has exited.
 */
VIM_RUNTIME_API vim_runtime_instance *VIM_RUNTIME_CALL
vim_runtime_instance_create(int argc, const char *const *argv);

/* Return 1 after the instance exits, 0 on timeout, -1 on error.  A successful
 * wait optionally writes Vim's exit status.  Do not wait on the owner thread.
 */
VIM_RUNTIME_API int VIM_RUNTIME_CALL
vim_runtime_instance_wait(vim_runtime_instance *instance,
				 unsigned long timeout_ms, int *exit_status);

/* Free a completed instance.  Return 1 when freed, 0 if still running,
 * or -1 on error.  The host must serialize wait/destroy calls on a handle.
 */
VIM_RUNTIME_API int VIM_RUNTIME_CALL
vim_runtime_instance_destroy(vim_runtime_instance *instance);

/* Borrow the native top-level GUI window, or NULL before it is created.
 * The pointer is an HWND on Windows and becomes invalid when Vim exits.
 */
VIM_RUNTIME_API void *VIM_RUNTIME_CALL
vim_runtime_instance_window(vim_runtime_instance *instance);

/* Ask the GUI instance to close through Vim's normal WM_CLOSE path.
 * Return 1 when posted, 0 before a GUI window exists, -1 on error.
 */
VIM_RUNTIME_API int VIM_RUNTIME_CALL
vim_runtime_instance_request_close(vim_runtime_instance *instance);

/* Queue a native Windows path for opening in this instance's GUI thread.
 * The path is copied before return.  Return 1 when queued, 0 until the GUI
 * window is ready, or -1 on invalid input or a stopped instance.
 * Queued requests are serialized and Vim may still reject an edit.
 */
VIM_RUNTIME_API int VIM_RUNTIME_CALL
vim_runtime_instance_open_file_w(vim_runtime_instance *instance,
                                const wchar_t *absolute_path);

#ifdef VIM_RUNTIME_LIBRARY
/* Internal exit landing for mch_exit_g() and mch_exit_c().  Keep the jump
 * entirely inside the Vim C worker thread: no C++ or Qt frame may be crossed.
 */
void vim_runtime_thread_exit(int exit_status);
void vim_runtime_thread_gui_ready(void);
void vim_runtime_console_cleanup(void);
void vim_runtime_thread_process_open_files(void);
void vim_runtime_thread_open_done(void *cookie);
unsigned long long vim_runtime_thread_serial(void);
#endif

#ifdef __cplusplus
}
#endif

#endif /* VIM_RUNTIME_API_H */
