/* popupwin.c */
int popup_on_border(win_T *wp, int row, int col);
int popup_close_if_on_X(win_T *wp, int row, int col);
void popup_start_drag(win_T *wp, int row, int col);
void popup_drag(win_T *wp);
void popup_set_firstline(win_T *wp);
int popup_is_in_scrollbar(win_T *wp, int row, int col);
void popup_handle_scrollbar_click(win_T *wp, int row, int col);
int popup_top_extra(win_T *wp);
int popup_left_extra(win_T *wp);
int popup_height(win_T *wp);
int popup_width(win_T *wp);
int popup_extra_width(win_T *wp);
int parse_previewpopup(win_T *wp);
int parse_completepopup(win_T *wp);
void popup_set_wantpos_cursor(win_T *wp, int width, dict_T *d);
void popup_set_wantpos_rowcol(win_T *wp, int row, int col);
void popup_redraw_all(void);
void f_popup_clear(typval_T *argvars, typval_T *rettv);
void f_popup_create(typval_T *argvars, typval_T *rettv);
void f_popup_atcursor(typval_T *argvars, typval_T *rettv);
void f_popup_beval(typval_T *argvars, typval_T *rettv);
void popup_close_with_retval(win_T *wp, int retval);
void popup_close_for_mouse_click(win_T *wp);
void popup_handle_mouse_moved(void);
void f_popup_filter_menu(typval_T *argvars, typval_T *rettv);
void f_popup_filter_yesno(typval_T *argvars, typval_T *rettv);
void f_popup_dialog(typval_T *argvars, typval_T *rettv);
void f_popup_menu(typval_T *argvars, typval_T *rettv);
void f_popup_notification(typval_T *argvars, typval_T *rettv);
void f_popup_close(typval_T *argvars, typval_T *rettv);
void popup_hide(win_T *wp);
void f_popup_hide(typval_T *argvars, typval_T *rettv);
void popup_show(win_T *wp);
void f_popup_show(typval_T *argvars, typval_T *rettv);
void f_popup_settext(typval_T *argvars, typval_T *rettv);
void f_popup_setbuf(typval_T *argvars, typval_T *rettv);
int error_if_popup_window(int also_with_term);
int popup_close(int id, int force);
int popup_close_tabpage(tabpage_T *tp, int id, int force);
void close_all_popups(int force);
void f_popup_move(typval_T *argvars, typval_T *rettv);
void f_popup_setoptions(typval_T *argvars, typval_T *rettv);
void f_popup_getpos(typval_T *argvars, typval_T *rettv);
void f_popup_list(typval_T *argvars, typval_T *rettv);
void f_popup_locate(typval_T *argvars, typval_T *rettv);
void f_popup_getoptions(typval_T *argvars, typval_T *rettv);
int error_if_term_popup_window(void);
void popup_reset_handled(int handled_flag);
win_T *find_next_popup(int lowest, int handled_flag);
int popup_do_filter(int c);
int popup_no_mapping(void);
void popup_check_cursor_pos(void);
void may_update_popup_mask(int type);
void may_update_popup_position(void);
void update_popups(void (*win_update)(win_T *wp));
int set_ref_in_popups(int copyID);
int popup_is_popup(win_T *wp);
win_T *popup_find_preview_window(void);
win_T *popup_find_info_window(void);
void f_popup_findecho(typval_T *argvars, typval_T *rettv);
void f_popup_findinfo(typval_T *argvars, typval_T *rettv);
void f_popup_findpreview(typval_T *argvars, typval_T *rettv);
int popup_create_preview_window(int info);
void popup_close_preview(void);
void popup_hide_info(void);
int popup_overlaps_cmdline(void);
void popup_close_info(void);
win_T *popup_get_message_win(void);
void popup_show_message_win(void);
int popup_message_win_visible(void);
void popup_hide_message_win(void);
void start_echowindow(int time_sec);
void end_echowindow(void);
int popup_win_closed(win_T *win);
void popup_set_title(win_T *wp);
void popup_update_preview_title(void);
/* vim: set ft=c : */
