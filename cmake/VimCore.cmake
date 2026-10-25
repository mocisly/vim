# Included from Vim's generated CMakeLists while its Vim target source lists
# are still in scope. This module and all integration sources live outside Vim.
target_include_directories(vim PRIVATE
    "${VIM_INTEGRATION_ROOT}/include"
    "${VIM_INTEGRATION_ROOT}/src/runtime/internal"
)
target_compile_definitions(vim PRIVATE FEAT_MBYTE_IME DYNAMIC_IME)

if(VIM_BUILD_SHARED_CORE)
    if(NOT WIN32)
        message(FATAL_ERROR "VIM_BUILD_SHARED_CORE currently requires Windows")
    endif()

    set(VIM_SHARED_SOURCE_FILES ${Source_Files})
    list(REMOVE_ITEM VIM_SHARED_SOURCE_FILES "src/os_w32exe.c")
    add_library(vim_shared_core SHARED
        ${Header_Files}
        ${Proto_Files}
        ${VIM_SHARED_SOURCE_FILES}
        "${VIM_INTEGRATION_ROOT}/src/runtime/vim_runtime_api.c"
        "${VIM_INTEGRATION_ROOT}/include/vim_runtime_api.h"
        "${VIM_INTEGRATION_ROOT}/src/runtime/internal/vim_instance_state.h"
    )
    target_include_directories(vim_shared_core PRIVATE
        $<TARGET_PROPERTY:vim,INCLUDE_DIRECTORIES>
    )
    target_compile_definitions(vim_shared_core PRIVATE
        $<TARGET_PROPERTY:vim,COMPILE_DEFINITIONS>
        VIMDLL
        VIM_RUNTIME_LIBRARY
        EXITFREE
    )
    target_compile_options(vim_shared_core PRIVATE
        $<TARGET_PROPERTY:vim,COMPILE_OPTIONS>
    )
    target_link_libraries(vim_shared_core PRIVATE
        libvterm
        xdiff
        ${Python3_LIBRARIES}
        "${ADDITIONAL_LIBRARY_DEPENDENCIES}"
    )

    get_target_property(VIM_MSVC_RUNTIME_LIBRARY vim MSVC_RUNTIME_LIBRARY)
    set_target_properties(vim_shared_core PROPERTIES
        OUTPUT_NAME vimcore
        MSVC_RUNTIME_LIBRARY "${VIM_MSVC_RUNTIME_LIBRARY}"
        INTERPROCEDURAL_OPTIMIZATION_RELEASE TRUE
        RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/Debug/vim"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release/vim"
        ARCHIVE_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/Debug/vim"
        ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release/vim"
    )
    if(MSVC)
        target_link_options(vim_shared_core PRIVATE
            $<$<CONFIG:Release>:/LTCG>
            /MANIFEST:NO
            /DEBUG
        )
    endif()
    add_custom_command(
        TARGET vim_shared_core
        PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E chdir ${CMAKE_CURRENT_SOURCE_DIR}/src ${CMAKE_CURRENT_SOURCE_DIR}/src/pathdef.bat ${CMAKE_BUILD_TYPE} ${CMAKE_VS_PLATFORM_NAME}
        COMMENT "Generate pathdef.c for the shared Vim core"
    )
endif()

if(VIM_ENABLE_QT_HOST)
    if(NOT VIM_BUILD_SHARED_CORE)
        message(FATAL_ERROR "VIM_ENABLE_QT_HOST requires VIM_BUILD_SHARED_CORE")
    endif()
    add_executable(vim_qt_host WIN32
        "${VIM_INTEGRATION_ROOT}/src/qt_host/main.cpp"
        "${VIM_INTEGRATION_ROOT}/include/vim_runtime_api.h"
    )
    target_include_directories(vim_qt_host PRIVATE "${VIM_INTEGRATION_ROOT}/include")
    target_link_libraries(vim_qt_host PRIVATE vim_shared_core)
    vim_configure_qt_host(vim_qt_host)
    set_target_properties(vim_qt_host PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/Debug/vim"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release/vim"
    )
endif()
