cmake_minimum_required(VERSION 3.16.0 FATAL_ERROR)

set(CMAKE_SYSTEM_VERSION 10.0 CACHE STRING "" FORCE)

project(vim C CXX)

set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT vim)

################################################################################
# Set target arch type if empty. Visual studio solution generator provides it.
################################################################################
if(NOT CMAKE_VS_PLATFORM_NAME)
    set(CMAKE_VS_PLATFORM_NAME "x64")
endif()
message("${CMAKE_VS_PLATFORM_NAME} architecture in use")

if(NOT ("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32"
     OR "${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64"))
    message(FATAL_ERROR "${CMAKE_VS_PLATFORM_NAME} arch is not supported!")
endif()

################################################################################
# Global configuration types
################################################################################
set(CMAKE_CONFIGURATION_TYPES
    "Debug"
    "Release"
    CACHE STRING "" FORCE
)

################################################################################
# Global compiler options
################################################################################
if(MSVC)
    # remove default flags provided with CMake for MSVC
    set(CMAKE_C_FLAGS "")
    set(CMAKE_C_FLAGS_DEBUG "")
    set(CMAKE_C_FLAGS_RELEASE "")
    set(CMAKE_CXX_FLAGS "")
    set(CMAKE_CXX_FLAGS_DEBUG "")
    set(CMAKE_CXX_FLAGS_RELEASE "")
endif()

################################################################################
# Global linker options
################################################################################
if(MSVC)
    # remove default flags provided with CMake for MSVC
    set(CMAKE_EXE_LINKER_FLAGS "")
    set(CMAKE_MODULE_LINKER_FLAGS "")
    set(CMAKE_SHARED_LINKER_FLAGS "")
    set(CMAKE_STATIC_LINKER_FLAGS "")
    set(CMAKE_EXE_LINKER_FLAGS_DEBUG "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_DEBUG "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_DEBUG "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_DEBUG "${CMAKE_STATIC_LINKER_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS}")
    set(CMAKE_MODULE_LINKER_FLAGS_RELEASE "${CMAKE_MODULE_LINKER_FLAGS}")
    set(CMAKE_SHARED_LINKER_FLAGS_RELEASE "${CMAKE_SHARED_LINKER_FLAGS}")
    set(CMAKE_STATIC_LINKER_FLAGS_RELEASE "${CMAKE_STATIC_LINKER_FLAGS}")
endif()

################################################################################
# Nuget packages function stub.
################################################################################
function(use_package TARGET PACKAGE VERSION)
    message(WARNING "No implementation of use_package. Create yours. "
                    "Package \"${PACKAGE}\" with version \"${VERSION}\" "
                    "for target \"${TARGET}\" is ignored!")
endfunction()

################################################################################
# Common utils
################################################################################
include(CMake/Utils.cmake)

################################################################################
# Additional Global Settings(add specific info there)
################################################################################
include(CMake/GlobalSettingsInclude.cmake OPTIONAL)

################################################################################
# Use solution folders feature
################################################################################
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

################################################################################
# Sub-projects
################################################################################



























set(PROJECT_NAME vim)

if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src/pathdef.bat ${CMAKE_BUILD_TYPE} ${CMAKE_VS_PLATFORM_NAME}
        RESULT_VARIABLE result
        )

    if(result EQUAL 0)
        message(STATUS "Command executed successfully")
    else()
        message(FATAL_ERROR "Command failed with error code ${result}")
    endif()
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    execute_process(
        COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src/pathdef.bat ${CMAKE_BUILD_TYPE} ${CMAKE_VS_PLATFORM_NAME}
        RESULT_VARIABLE result
        )

    if(result EQUAL 0)
        message(STATUS "Command executed successfully")
    else()
        message(FATAL_ERROR "Command failed with error code ${result}")
    endif()
endif()

################################################################################
# Source groups
################################################################################
set(Header_Files
    "src/alloc.h"
    #"src/arabic.h"
    "src/ascii.h"
    "src/beval.h"
    "src/dosinst.h"
    "src/errors.h"
    "src/ex_cmdidxs.h"
    "src/ex_cmds.h"
    "src/feature.h"
    #"src/glbl_ime.h"
    "src/globals.h"
    "src/gui.h"
    #"src/gui_at_sb.h"
    #"src/gui_beval.h"
    "src/gui_dwrite.h"
    "src/gui_gtk_f.h"
    "src/gui_gtk_vms.h"
    "src/gui_w32_rc.h"
    "src/gui_x11_pm.h"
    "src/gui_xmebw.h"
    "src/gui_xmebwp.h"
    #"src/guiw16rc.h"
    #"src/if_cscope.h"
    "src/if_mzsch.h"
    "src/if_ole.h"
    "src/if_py_both.h"
    #"src/if_sniff.h"
    #"src/integration.h"
    "src/iscygpty.h"
    "src/keymap.h"
    "src/macros.h"
    "src/nbdebug.h"
    "src/option.h"
    "src/optiondefs.h"
    "src/os_amiga.h"
    #"src/os_beos.h"
    "src/os_dos.h"
    "src/os_mac.h"
    #"src/os_mint.h"
    #"src/os_msdos.h"
    #"src/os_os2_cfg.h"
    "src/os_qnx.h"
    "src/os_unix.h"
    "src/os_unixx.h"
    "src/os_vms_conf.h"
    #"src/os_win16.h"
    "src/os_win32.h"
    "src/proto.h"
    "src/protodef.h"
    "src/regexp.h"
    "src/spell.h"
    "src/structs.h"
    #"src/term.h"
    "src/version.h"
    "src/vim.h"
    "src/vim9.h"
    #"src/vimio.h"
    #"src/vimtbar.h"
    #"src/workshop.h"
    #"src/wsdebug.h"
    "src/xpm_w32.h"
)
source_group("Header Files" FILES ${Header_Files})

set(Proto_Files
    "src/proto/arabic.pro"
    "src/proto/arglist.pro"
    "src/proto/autocmd.pro"
    "src/proto/beval.pro"
    "src/proto/blob.pro"
    "src/proto/blowfish.pro"
    "src/proto/buffer.pro"
    "src/proto/bufwrite.pro"
    "src/proto/change.pro"
    "src/proto/channel.pro"
    "src/proto/charset.pro"
    "src/proto/cindent.pro"
    "src/proto/clientserver.pro"
    "src/proto/clipboard.pro"
    "src/proto/cmdexpand.pro"
    "src/proto/cmdhist.pro"
    "src/proto/crypt.pro"
    "src/proto/crypt_zip.pro"
    "src/proto/debugger.pro"
    "src/proto/dict.pro"
    "src/proto/diff.pro"
    "src/proto/digraph.pro"
    "src/proto/drawline.pro"
    "src/proto/drawscreen.pro"
    "src/proto/edit.pro"
    "src/proto/eval.pro"
    "src/proto/evalbuffer.pro"
    "src/proto/evalfunc.pro"
    "src/proto/evalvars.pro"
    "src/proto/evalwindow.pro"
    "src/proto/ex_cmds.pro"
    "src/proto/ex_cmds2.pro"
    "src/proto/ex_docmd.pro"
    "src/proto/ex_eval.pro"
    "src/proto/ex_getln.pro"
    #"src/proto/farsi.pro"
    "src/proto/fileio.pro"
    "src/proto/filepath.pro"
    "src/proto/findfile.pro"
    "src/proto/fold.pro"
    "src/proto/getchar.pro"
    "src/proto/gui.pro"
    #"src/proto/gui_athena.pro"
    "src/proto/gui_beval.pro"
    "src/proto/gui_gtk.pro"
    "src/proto/gui_gtk_gresources.pro"
    "src/proto/gui_gtk_x11.pro"
    "src/proto/gui_haiku.pro"
    #"src/proto/gui_mac.pro"
    "src/proto/gui_motif.pro"
    "src/proto/gui_photon.pro"
    #"src/proto/gui_riscos.pro"
    #"src/proto/gui_w16.pro"
    "src/proto/gui_w32.pro"
    "src/proto/gui_x11.pro"
    "src/proto/gui_xim.pro"
    "src/proto/gui_xmdlg.pro"
    #"src/proto/hangulin.pro"
    "src/proto/hardcopy.pro"
    "src/proto/hashtab.pro"
    "src/proto/help.pro"
    "src/proto/highlight.pro"
    #"src/proto/if_bore.pro"
    "src/proto/if_cscope.pro"
    "src/proto/if_lua.pro"
    "src/proto/if_mzsch.pro"
    "src/proto/if_ole.pro"
    "src/proto/if_perl.pro"
    "src/proto/if_perlsfio.pro"
    "src/proto/if_python.pro"
    "src/proto/if_python3.pro"
    "src/proto/if_ruby.pro"
    "src/proto/if_tcl.pro"
    "src/proto/if_xcmdsrv.pro"
    "src/proto/indent.pro"
    "src/proto/insexpand.pro"
    "src/proto/job.pro"
    "src/proto/json.pro"
    "src/proto/linematch.pro"
    "src/proto/list.pro"
    "src/proto/locale.pro"
    "src/proto/main.pro"
    "src/proto/map.pro"
    "src/proto/mark.pro"
    "src/proto/match.pro"
    "src/proto/mbyte.pro"
    "src/proto/memfile.pro"
    "src/proto/memline.pro"
    "src/proto/menu.pro"
    "src/proto/message.pro"
    "src/proto/misc1.pro"
    "src/proto/misc2.pro"
    "src/proto/mouse.pro"
    "src/proto/move.pro"
    "src/proto/netbeans.pro"
    "src/proto/normal.pro"
    "src/proto/ops.pro"
    "src/proto/option.pro"
    "src/proto/optionstr.pro"
    "src/proto/os_amiga.pro"
    "src/proto/os_mac_conv.pro"
    #"src/proto/os_msdos.pro"
    "src/proto/os_mswin.pro"
    "src/proto/os_qnx.pro"
    #"src/proto/os_riscos.pro"
    "src/proto/os_unix.pro"
    "src/proto/os_vms.pro"
    #"src/proto/os_win16.pro"
    "src/proto/os_win32.pro"
    "src/proto/popupmenu.pro"
    #"src/proto/popupmnu.pro"
    "src/proto/popupwin.pro"
    "src/proto/profiler.pro"
    "src/proto/pty.pro"
    "src/proto/quickfix.pro"
    #"src/proto/quickfix.pro.orig"
    "src/proto/regexp.pro"
    "src/proto/register.pro"
    "src/proto/screen.pro"
    "src/proto/scriptfile.pro"
    "src/proto/search.pro"
    "src/proto/session.pro"
    "src/proto/sha256.pro"
    "src/proto/sign.pro"
    "src/proto/sound.pro"
    "src/proto/spell.pro"
    "src/proto/spellfile.pro"
    "src/proto/spellsuggest.pro"
    "src/proto/syntax.pro"
    "src/proto/tag.pro"
    "src/proto/term.pro"
    "src/proto/terminal.pro"
    "src/proto/termlib.pro"
    "src/proto/testing.pro"
    "src/proto/textformat.pro"
    "src/proto/textobject.pro"
    "src/proto/textprop.pro"
    "src/proto/time.pro"
    "src/proto/tuple.pro"
    "src/proto/typval.pro"
    "src/proto/ui.pro"
    "src/proto/undo.pro"
    "src/proto/usercmd.pro"
    "src/proto/userfunc.pro"
    "src/proto/version.pro"
    "src/proto/vim9cmds.pro"
    "src/proto/vim9compile.pro"
    "src/proto/vim9execute.pro"
    "src/proto/vim9expr.pro"
    "src/proto/vim9instr.pro"
    "src/proto/vim9script.pro"
    "src/proto/vim9type.pro"
    "src/proto/viminfo.pro"
    "src/proto/winclip.pro"
    "src/proto/window.pro"
    #"src/proto/workshop.pro"
)
source_group("Proto Files" FILES ${Proto_Files})

set(Resource_Files
    "src/vim.exe.mnf"
    "src/vim.rc"
    #"src/gvim.exe.mnf"
)
source_group("Resource Files" FILES ${Resource_Files})

set(Source_Files
    "src/alloc.c"
    "src/arabic.c"
    "src/arglist.c"
    "src/autocmd.c"
    "src/auto/pathdef.c"
    "src/beval.c"
    "src/blob.c"
    "src/blowfish.c"
    "src/buffer.c"
    "src/bufwrite.c"
    "src/change.c"
    "src/channel.c"
    "src/charset.c"
    "src/cindent.c"
    "src/clientserver.c"
    "src/clipboard.c"
    "src/cmdexpand.c"
    "src/cmdhist.c"
    "src/crypt.c"
    "src/crypt_zip.c"
    "src/debugger.c"
    "src/dict.c"
    "src/diff.c"
    "src/digraph.c"
    "src/drawline.c"
    "src/drawscreen.c"
    "src/edit.c"
    "src/eval.c"
    "src/evalbuffer.c"
    "src/evalfunc.c"
    "src/evalvars.c"
    "src/evalwindow.c"
    "src/ex_cmds.c"
    "src/ex_cmds2.c"
    "src/ex_docmd.c"
    "src/ex_eval.c"
    "src/ex_getln.c"
    "src/fileio.c"
    "src/filepath.c"
    "src/findfile.c"
    "src/float.c"
    "src/fold.c"
    "src/getchar.c"
    "src/gc.c"
    "src/gui.c"
    "src/gui_beval.c"
    "src/gui_dwrite.cpp"
    "src/gui_w32.c"
    "src/gui_xim.c"
    "src/hardcopy.c"
    "src/hashtab.c"
    "src/help.c"
    "src/highlight.c"
    "src/if_cscope.c"
    "src/indent.c"
    "src/insexpand.c"
    "src/iscygpty.c"
    "src/job.c"
    "src/json.c"
    "src/linematch.c"
    "src/list.c"
    "src/locale.c"
    "src/logfile.c"
    "src/main.c"
    "src/map.c"
    "src/mark.c"
    "src/match.c"
    "src/mbyte.c"
    "src/memfile.c"
    "src/memline.c"
    "src/menu.c"
    "src/message.c"
    "src/misc1.c"
    "src/misc2.c"
    "src/mouse.c"
    "src/move.c"
    "src/nbdebug.c"
    "src/normal.c"
    "src/ops.c"
    "src/option.c"
    "src/optionstr.c"
    "src/os_mswin.c"
    "src/os_w32dll.c"
    "src/os_w32exe.c"
    "src/os_win32.c"
    "src/popupmenu.c"
    "src/popupwin.c"
    "src/profiler.c"
    "src/quickfix.c"
    "src/regexp.c"
    "src/register.c"
    "src/screen.c"
    "src/scriptfile.c"
    "src/search.c"
    "src/session.c"
    "src/sha256.c"
    "src/sign.c"
    "src/sound.c"
    "src/spell.c"
    "src/spellfile.c"
    "src/spellsuggest.c"
    "src/strings.c"
    "src/syntax.c"
    "src/tag.c"
    "src/term.c"
    "src/terminal.c"
    "src/testing.c"
    "src/textformat.c"
    "src/textobject.c"
    "src/textprop.c"
    "src/time.c"
    "src/tuple.c"
    "src/typval.c"
    "src/ui.c"
    "src/undo.c"
    "src/usercmd.c"
    "src/userfunc.c"
    "src/version.c"
    "src/vim9class.c"
    "src/vim9cmds.c"
    "src/vim9compile.c"
    "src/vim9execute.c"
    "src/vim9expr.c"
    "src/vim9instr.c"
    "src/vim9script.c"
    "src/vim9type.c"
    "src/viminfo.c"
    "src/winclip.c"
    "src/window.c"
)
source_group("Source Files" FILES ${Source_Files})

#set(bore
#    "src/if_bore.c"
#    "src/if_bore.h"
#    "src/if_bore_find.cpp"
#)
#source_group("bore" FILES ${bore})

set(ALL_FILES
    ${Header_Files}
    ${Proto_Files}
    ${Resource_Files}
    ${Source_Files}
    #    ${bore}
)

################################################################################
# Target
################################################################################
add_executable(${PROJECT_NAME} ${ALL_FILES})

use_props(${PROJECT_NAME} "${CMAKE_CONFIGURATION_TYPES}" "${DEFAULT_CXX_PROPS}")
set_target_properties(${PROJECT_NAME} PROPERTIES
    VS_GLOBAL_KEYWORD "Win32Proj"
)
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        COMMON_LANGUAGE_RUNTIME_RELEASE "No"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        COMMON_LANGUAGE_RUNTIME_RELEASE "No"
    )
endif()
################################################################################
# Target name
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        TARGET_NAME_DEBUG   "vimd32"
        TARGET_NAME_RELEASE "vim32"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        TARGET_NAME_DEBUG   "vimd"
        TARGET_NAME_RELEASE "vim"
    )
endif()
################################################################################
# Output directory
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_DIRECTORY_DEBUG   "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/"
        OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_DIRECTORY_DEBUG   "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}"
        OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/${CMAKE_BUILD_TYPE}/"
    )
endif()

################################################################################
# MSVC runtime library
################################################################################
get_property(MSVC_RUNTIME_LIBRARY_DEFAULT TARGET ${PROJECT_NAME} PROPERTY MSVC_RUNTIME_LIBRARY)
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    string(CONCAT "MSVC_RUNTIME_LIBRARY_STR"
        $<$<CONFIG:Debug>:
            MultiThreadedDebugDLL
        >
        $<$<NOT:$<OR:$<CONFIG:Debug>>>:${MSVC_RUNTIME_LIBRARY_DEFAULT}>
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    string(CONCAT "MSVC_RUNTIME_LIBRARY_STR"
        $<$<CONFIG:Debug>:
            MultiThreadedDebugDLL
        >
        $<$<NOT:$<OR:$<CONFIG:Debug>>>:${MSVC_RUNTIME_LIBRARY_DEFAULT}>
    )
endif()
set_target_properties(${PROJECT_NAME} PROPERTIES MSVC_RUNTIME_LIBRARY ${MSVC_RUNTIME_LIBRARY_STR})

################################################################################
# Include directories
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    target_include_directories(${PROJECT_NAME} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/.;"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/proto;"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/libvterm/include"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    target_include_directories(${PROJECT_NAME} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/.;"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/proto;"
        "${CMAKE_CURRENT_SOURCE_DIR}/src/libvterm/include"
    )
endif()

################################################################################
# Compile definitions
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "$<$<CONFIG:Debug>:"
            ""
        ">"
        "$<$<CONFIG:Release>:"
            "NDEBUG"
        ">"
        "WIN32;"
        "WINVER=0x0601;"
        "_WIN32_WINNT=0x0601;"
        "_CRT_NONSTDC_NO_DEPRECATE;"
        "_CRT_SECURE_NO_WARNINGS;"
        "_WINSOCK_DEPRECATED_NO_WARNINGS;"
        "HAVE_STDINT_H;"
        "HAVE_PATHDEF;"
        "FEAT_GUI_MSWIN;"
        "FEAT_DIRECTX;"
        "DYNAMIC_DIRECTX;"
        "FEAT_DIRECTX_COLOR_EMOJI;"
        "DYNAMIC_ICONV;"
        "DYNAMIC_GETTEXT;"
        "FEAT_BIG;"
        "FEAT_PROFILE;"
        "FEAT_JOB_CHANNEL;"
        "FEAT_TERMINAL;"
        #"FEAT_BORE;"
        "VSNPRINTF=vim_vsnprintf;"
        "SNPRINTF=vim_snprintf"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "$<$<CONFIG:Debug>:"
            ""
        ">"
        "$<$<CONFIG:Release>:"
            "NDEBUG"
        ">"
        "WIN32;"
        "WINVER=0x0601;"
        "_WIN32_WINNT=0x0601;"
        "_CRT_NONSTDC_NO_DEPRECATE;"
        "_CRT_SECURE_NO_WARNINGS;"
        "_WINSOCK_DEPRECATED_NO_WARNINGS;"
        "HAVE_STDINT_H;"
        "HAVE_PATHDEF;"
        "FEAT_GUI_MSWIN;"
        "FEAT_DIRECTX;"
        "DYNAMIC_DIRECTX;"
        "FEAT_DIRECTX_COLOR_EMOJI;"
        "DYNAMIC_ICONV;"
        "DYNAMIC_GETTEXT;"
        "FEAT_BIG;"
        "FEAT_PROFILE;"
        "FEAT_JOB_CHANNEL;"
        "FEAT_TERMINAL;"
        #"FEAT_BORE;"
        "VSNPRINTF=vim_vsnprintf;"
        "SNPRINTF=vim_snprintf"
    )
endif()

################################################################################
# Compile and link options
################################################################################
if(MSVC)
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /Od;
                ${DEFAULT_CXX_EXCEPTION_HANDLING}
            >
            $<$<CONFIG:Release>:
                /GL;
                /Ox;
                /Ob2;
                /Oi;
                /Oy;
                /Ot;
                /GS-
            >
            /MP;
            /Gm-;
            /W3;
            /Zi;
            /source-charset:utf-8
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /Od;
                ${DEFAULT_CXX_EXCEPTION_HANDLING}
            >
            $<$<CONFIG:Release>:
                /GL;
                /Ox;
                /Ob2;
                /Oi;
                /Oy;
                /Ot;
                /GS-
            >
            /MP;
            /Gm-;
            /W3;
            /Zi;
            /source-charset:utf-8
        )
    endif()
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        string(CONCAT FILE_CL_OPTIONS
            "/wd4996"
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        string(CONCAT FILE_CL_OPTIONS
            "/wd4996"
        )
    endif()
    source_file_compile_options(os_win32.c ${FILE_CL_OPTIONS})
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /INCREMENTAL
            >
            $<$<CONFIG:Release>:
                /OPT:REF;
                /LTCG;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            /MANIFEST:NO;
            /STACK:8388608;
            /DEBUG;
            /MACHINE:X86;
            /SUBSYSTEM:WINDOWS;
            /cgthreads:8
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /INCREMENTAL
            >
            $<$<CONFIG:Release>:
                /OPT:REF;
                /LTCG;
                /OPT:ICF;
                /INCREMENTAL:NO
            >
            /MANIFEST:NO;
            /STACK:8388608;
            /DEBUG;
            /SUBSYSTEM:WINDOWS;
            /cgthreads:8
        )
    endif()
endif()

################################################################################
# Pre build events
################################################################################
#if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
#    add_custom_command(
#        TARGET ${PROJECT_NAME}
#        PRE_BUILD
#        COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src/pathdef.bat ${CMAKE_BUILD_TYPE} ${CMAKE_VS_PLATFORM_NAME}
#        COMMENT "Generate pathdef.c"
#    )
#elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
#    add_custom_command(
#        TARGET ${PROJECT_NAME}
#        PRE_BUILD
#        COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src/pathdef.bat ${CMAKE_BUILD_TYPE} ${CMAKE_VS_PLATFORM_NAME}
#        COMMENT "Generate pathdef.c"
#    )
#endif()



################################################################################
# Dependencies
################################################################################
# Link with other targets.
target_link_libraries(${PROJECT_NAME} PRIVATE
    libvterm
    xdiff
)

if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set(ADDITIONAL_LIBRARY_DEPENDENCIES
        "version;"
        "comctl32;"
        "kernel32;"
        "user32;"
        "gdi32;"
        "winspool;"
        "comdlg32;"
        "advapi32;"
        "shell32;"
        "ole32;"
        "oleaut32;"
        "uuid;"
        "odbc32;"
        "odbccp32;"
        "WSock32;"
        "Netapi32"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set(ADDITIONAL_LIBRARY_DEPENDENCIES
        "version;"
        "comctl32;"
        "kernel32;"
        "user32;"
        "gdi32;"
        "winspool;"
        "comdlg32;"
        "advapi32;"
        "shell32;"
        "ole32;"
        "oleaut32;"
        "uuid;"
        "odbc32;"
        "odbccp32;"
        "WSock32;"
        "Netapi32"
    )
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE "${ADDITIONAL_LIBRARY_DEPENDENCIES}")



























set(PROJECT_NAME libvterm)

################################################################################
# Source groups
################################################################################
set(Header_Files
    "src/libvterm/include/vterm.h"
    "src/libvterm/include/vterm_keycodes.h"
    "src/libvterm/src/rect.h"
    "src/libvterm/src/utf8.h"
    "src/libvterm/src/vterm_internal.h"
)
source_group("Header Files" FILES ${Header_Files})

set(Source_Files
    "src/libvterm/src/encoding.c"
    "src/libvterm/src/keyboard.c"
    "src/libvterm/src/mouse.c"
    "src/libvterm/src/parser.c"
    "src/libvterm/src/pen.c"
    "src/libvterm/src/screen.c"
    "src/libvterm/src/state.c"
    "src/libvterm/src/unicode.c"
    "src/libvterm/src/vterm.c"
)
source_group("Source Files" FILES ${Source_Files})

set(ALL_FILES
    ${Header_Files}
    ${Source_Files}
)

################################################################################
# Target
################################################################################
add_library(${PROJECT_NAME} STATIC ${ALL_FILES})

use_props(${PROJECT_NAME} "${CMAKE_CONFIGURATION_TYPES}" "${DEFAULT_CXX_PROPS}")
set(ROOT_NAMESPACE libvterm)

set_target_properties(${PROJECT_NAME} PROPERTIES
    VS_GLOBAL_KEYWORD "Win32Proj"
)
################################################################################
# Output directory
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_DIRECTORY_DEBUG   "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
        OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_DIRECTORY_DEBUG   "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
        OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
    )
endif()
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION_RELEASE "TRUE"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION_RELEASE "TRUE"
    )
endif()
################################################################################
# Include directories
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    target_include_directories(${PROJECT_NAME} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/libvterm/include"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    target_include_directories(${PROJECT_NAME} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/libvterm/include"
    )
endif()

################################################################################
# Compile definitions
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "$<$<CONFIG:Debug>:"
            "_DEBUG"
        ">"
        "$<$<CONFIG:Release>:"
            "NDEBUG"
        ">"
        "WIN32;"
        "_LIB;"
        "INLINE=;"
        "VSNPRINTF=vim_vsnprintf;"
        "IS_COMBINING_FUNCTION=utf_iscomposing_uint;"
        "WCWIDTH_FUNCTION=utf_uint2cells;"
        "_CRT_SECURE_NO_WARNINGS;"
        "UNICODE;"
        "_UNICODE"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "$<$<CONFIG:Debug>:"
            "_DEBUG"
        ">"
        "$<$<CONFIG:Release>:"
            "NDEBUG"
        ">"
        "_LIB;"
        "INLINE=;"
        "VSNPRINTF=vim_vsnprintf;"
        "IS_COMBINING_FUNCTION=utf_iscomposing_uint;"
        "WCWIDTH_FUNCTION=utf_uint2cells;"
        "_CRT_SECURE_NO_WARNINGS;"
        "UNICODE;"
        "_UNICODE"
    )
endif()

################################################################################
# Compile and link options
################################################################################
if(MSVC)
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /Od
            >
            $<$<CONFIG:Release>:
                /O2;
                /Oi;
                /Gy
            >
            /W3;
            ${DEFAULT_CXX_DEBUG_INFORMATION_FORMAT};
            ${DEFAULT_CXX_EXCEPTION_HANDLING};
            /Y-
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /Od
            >
            $<$<CONFIG:Release>:
                /O2;
                /Oi;
                /Gy
            >
            /W3;
            ${DEFAULT_CXX_DEBUG_INFORMATION_FORMAT};
            ${DEFAULT_CXX_EXCEPTION_HANDLING};
            /Y-
        )
    endif()
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Release>:
                /OPT:REF;
                /OPT:ICF
            >
            /SUBSYSTEM:WINDOWS
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Release>:
                /OPT:REF;
                /OPT:ICF
            >
            /SUBSYSTEM:WINDOWS
        )
    endif()
endif()



























set(PROJECT_NAME xdiff)

################################################################################
# Source groups
################################################################################
set(Header_Files
    "src/xdiff/xdiff.h"
    "src/xdiff/xdiffi.h"
    "src/xdiff/xemit.h"
    "src/xdiff/xinclude.h"
    "src/xdiff/xmacros.h"
    "src/xdiff/xprepare.h"
    "src/xdiff/xtypes.h"
    "src/xdiff/xutils.h"
)
source_group("Header Files" FILES ${Header_Files})

set(Source_Files
    "src/xdiff/xdiffi.c"
    "src/xdiff/xemit.c"
    "src/xdiff/xhistogram.c"
    "src/xdiff/xpatience.c"
    "src/xdiff/xprepare.c"
    "src/xdiff/xutils.c"
)
source_group("Source Files" FILES ${Source_Files})

set(ALL_FILES
    ${Header_Files}
    ${Source_Files}
)

################################################################################
# Target
################################################################################
add_library(${PROJECT_NAME} STATIC ${ALL_FILES})

use_props(${PROJECT_NAME} "${CMAKE_CONFIGURATION_TYPES}" "${DEFAULT_CXX_PROPS}")
set(ROOT_NAMESPACE xdiff)

set_target_properties(${PROJECT_NAME} PROPERTIES
    VS_GLOBAL_KEYWORD "Win32Proj"
)
################################################################################
# Output directory
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_DIRECTORY_DEBUG   "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
        OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        OUTPUT_DIRECTORY_DEBUG   "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
        OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/ObjVS${CMAKE_VS_PLATFORM_NAME}/$<CONFIG>/${PROJECT_NAME}/"
    )
endif()
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION_RELEASE "TRUE"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    set_target_properties(${PROJECT_NAME} PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION_RELEASE "TRUE"
    )
endif()
################################################################################
# Include directories
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    target_include_directories(${PROJECT_NAME} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/proto"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    target_include_directories(${PROJECT_NAME} PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/src/proto"
    )
endif()

################################################################################
# Compile definitions
################################################################################
if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "$<$<CONFIG:Debug>:"
            "_DEBUG"
        ">"
        "$<$<CONFIG:Release>:"
            "NDEBUG"
        ">"
        "WIN32;"
        "_LIB;"
        "UNICODE;"
        "_UNICODE"
    )
elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
    target_compile_definitions(${PROJECT_NAME} PRIVATE
        "$<$<CONFIG:Debug>:"
            "_DEBUG"
        ">"
        "$<$<CONFIG:Release>:"
            "NDEBUG"
        ">"
        "_LIB;"
        "UNICODE;"
        "_UNICODE"
    )
endif()

################################################################################
# Compile and link options
################################################################################
if(MSVC)
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /Od
            >
            $<$<CONFIG:Release>:
                /O2;
                /Oi;
                /Gy
            >
            /W3;
            ${DEFAULT_CXX_DEBUG_INFORMATION_FORMAT};
            ${DEFAULT_CXX_EXCEPTION_HANDLING};
            /Y-
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_compile_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Debug>:
                /Od
            >
            $<$<CONFIG:Release>:
                /O2;
                /Oi;
                /Gy
            >
            /W3;
            ${DEFAULT_CXX_DEBUG_INFORMATION_FORMAT};
            ${DEFAULT_CXX_EXCEPTION_HANDLING};
            /Y-
        )
    endif()
    if("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "Win32")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Release>:
                /OPT:REF;
                /OPT:ICF
            >
            /SUBSYSTEM:WINDOWS
        )
    elseif("${CMAKE_VS_PLATFORM_NAME}" STREQUAL "x64")
        target_link_options(${PROJECT_NAME} PRIVATE
            $<$<CONFIG:Release>:
                /OPT:REF;
                /OPT:ICF
            >
            /SUBSYSTEM:WINDOWS
        )
    endif()
endif()

set(OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}")

file(COPY "${CMAKE_SOURCE_DIR}/runtime" DESTINATION "${OUTPUT_DIR}")
