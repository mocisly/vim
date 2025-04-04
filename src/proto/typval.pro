/* typval.c */
typval_T *alloc_tv(void);
typval_T *alloc_string_tv(char_u *s);
void free_tv(typval_T *varp);
void clear_tv(typval_T *varp);
void init_tv(typval_T *varp);
varnumber_T tv_get_number(typval_T *varp);
varnumber_T tv_to_number(typval_T *varp);
varnumber_T tv_get_number_chk(typval_T *varp, int *denote);
varnumber_T tv_get_bool(typval_T *varp);
varnumber_T tv_get_bool_chk(typval_T *varp, int *denote);
float_T tv_get_float(typval_T *varp);
int check_for_unknown_arg(typval_T *args, int idx);
int check_for_string_arg(typval_T *args, int idx);
int check_for_nonempty_string_arg(typval_T *args, int idx);
int check_for_opt_string_arg(typval_T *args, int idx);
int check_for_number_arg(typval_T *args, int idx);
int check_for_opt_number_arg(typval_T *args, int idx);
int check_for_float_or_nr_arg(typval_T *args, int idx);
int check_for_bool_arg(typval_T *args, int idx);
int check_for_opt_bool_arg(typval_T *args, int idx);
int check_for_opt_bool_or_number_arg(typval_T *args, int idx);
int check_for_blob_arg(typval_T *args, int idx);
int check_for_list_arg(typval_T *args, int idx);
int check_for_nonnull_list_arg(typval_T *args, int idx);
int check_for_opt_list_arg(typval_T *args, int idx);
int check_for_tuple_arg(typval_T *args, int idx);
int check_for_dict_arg(typval_T *args, int idx);
int check_for_nonnull_dict_arg(typval_T *args, int idx);
int check_for_opt_dict_arg(typval_T *args, int idx);
int check_for_opt_nonnull_dict_arg(typval_T *args, int idx);
int check_for_chan_or_job_arg(typval_T *args, int idx);
int check_for_opt_chan_or_job_arg(typval_T *args, int idx);
int check_for_job_arg(typval_T *args, int idx);
int check_for_opt_job_arg(typval_T *args, int idx);
int check_for_string_or_number_arg(typval_T *args, int idx);
int check_for_opt_string_or_number_arg(typval_T *args, int idx);
int check_for_buffer_arg(typval_T *args, int idx);
int check_for_opt_buffer_arg(typval_T *args, int idx);
int check_for_lnum_arg(typval_T *args, int idx);
int check_for_opt_lnum_arg(typval_T *args, int idx);
int check_for_string_or_blob_arg(typval_T *args, int idx);
int check_for_string_or_list_arg(typval_T *args, int idx);
int check_for_string_or_list_or_tuple_or_blob_arg(typval_T *args, int idx);
int check_for_opt_string_or_list_arg(typval_T *args, int idx);
int check_for_string_or_dict_arg(typval_T *args, int idx);
int check_for_string_or_number_or_list_arg(typval_T *args, int idx);
int check_for_opt_string_or_number_or_list_arg(typval_T *args, int idx);
int check_for_repeat_func_arg(typval_T *args, int idx);
int check_for_string_list_tuple_or_dict_arg(typval_T *args, int idx);
int check_for_string_or_func_arg(typval_T *args, int idx);
int check_for_list_or_blob_arg(typval_T *args, int idx);
int check_for_list_or_tuple_arg(typval_T *args, int idx);
int check_for_list_or_tuple_or_blob_arg(typval_T *args, int idx);
int check_for_list_or_tuple_or_dict_arg(typval_T *args, int idx);
int check_for_list_or_dict_or_blob_arg(typval_T *args, int idx);
int check_for_list_tuple_dict_blob_or_string_arg(typval_T *args, int idx);
int check_for_opt_buffer_or_dict_arg(typval_T *args, int idx);
int check_for_object_arg(typval_T *args, int idx);
int check_for_class_or_typealias_args(typval_T *args, int idx);
char_u *tv_get_string(typval_T *varp);
char_u *tv_get_string_strict(typval_T *varp);
char_u *tv_get_string_buf(typval_T *varp, char_u *buf);
char_u *tv_get_string_chk(typval_T *varp);
char_u *tv_get_string_buf_chk(typval_T *varp, char_u *buf);
char_u *tv_get_string_buf_chk_strict(typval_T *varp, char_u *buf, int strict);
char_u *tv_stringify(typval_T *varp, char_u *buf);
int tv_check_lock(typval_T *tv, char_u *name, int use_gettext);
void copy_tv(typval_T *from, typval_T *to);
int typval_compare(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic);
int typval_compare_list(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic, int *res);
int typval_compare_tuple(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic, int *res);
int typval_compare_null(typval_T *tv1, typval_T *tv2);
int typval_compare_blob(typval_T *tv1, typval_T *tv2, exprtype_T type, int *res);
int typval_compare_object(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic, int *res);
int typval_compare_dict(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic, int *res);
int typval_compare_func(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic, int *res);
int typval_compare_string(typval_T *tv1, typval_T *tv2, exprtype_T type, int ic, int *res);
char_u *typval_tostring(typval_T *arg, int quotes);
int tv_islocked(typval_T *tv);
int tv_equal(typval_T *tv1, typval_T *tv2, int ic);
int eval_option(char_u **arg, typval_T *rettv, int evaluate);
int eval_number(char_u **arg, typval_T *rettv, int evaluate, int want_string);
int eval_string(char_u **arg, typval_T *rettv, int evaluate, int interpolate);
int eval_lit_string(char_u **arg, typval_T *rettv, int evaluate, int interpolate);
int eval_interp_string(char_u **arg, typval_T *rettv, int evaluate);
char_u *tv2string(typval_T *tv, char_u **tofree, char_u *numbuf, int copyID);
int eval_env_var(char_u **arg, typval_T *rettv, int evaluate);
linenr_T tv_get_lnum(typval_T *argvars);
linenr_T tv_get_lnum_buf(typval_T *argvars, buf_T *buf);
buf_T *tv_get_buf(typval_T *tv, int curtab_only);
buf_T *tv_get_buf_from_arg(typval_T *tv);
/* vim: set ft=c : */
