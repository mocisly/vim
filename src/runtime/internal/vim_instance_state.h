/* vi:set ts=8 sts=4 sw=4 noet:
 *
 * Mutable buffer and window bookkeeping owned by the active Vim instance.
 * This is an internal slice of instance state, not a complete Vim context.
 * Activating one of these states alone does not isolate a Vim session: the
 * remaining global and file-static state must be switched together with it.
 * Include this header after vim.h for garray_T and hashtab_T.
 */

#ifndef VIM_INSTANCE_STATE_H
#define VIM_INSTANCE_STATE_H

typedef struct vim_instance_state_S
{
    int		buf_free_count;
    int		top_file_num;
    garray_T	buf_reuse;
    hashtab_T	buf_hashtab;
    int		last_win_id;
} vim_instance_state_T;

void vim_instance_state_init(vim_instance_state_T *state);
vim_instance_state_T *vim_instance_state_current(void);
vim_instance_state_T *vim_instance_state_activate(vim_instance_state_T *state);

#endif // VIM_INSTANCE_STATE_H
