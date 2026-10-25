function(vim_prepare_source output_variable)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
    set(vim_source_dir "${CMAKE_BINARY_DIR}/vim-source")
    execute_process(
        COMMAND "${Python3_EXECUTABLE}"
            "${VIM_INTEGRATION_ROOT}/tools/prepare_vim_source.py"
            --repo "${VIM_INTEGRATION_ROOT}"
            --upstream "${VIM_UPSTREAM_SOURCE_DIR}"
            --build-root "${CMAKE_BINARY_DIR}"
            "${VIM_INTEGRATION_ROOT}/patches/vim/0001-instance-state.patch"
            "${VIM_INTEGRATION_ROOT}/patches/vim/0002-cmake-integration.patch"
            "${VIM_INTEGRATION_ROOT}/patches/vim/0003-runtime-assets.patch"
            "${VIM_INTEGRATION_ROOT}/patches/vim/0004-open-file-api.patch"
        RESULT_VARIABLE preparation_status
        OUTPUT_VARIABLE preparation_output
        ERROR_VARIABLE preparation_error
    )
    if(NOT preparation_status EQUAL 0)
        message(FATAL_ERROR "Cannot prepare Vim source:\n${preparation_error}")
    endif()
    string(STRIP "${preparation_output}" preparation_output)
    message(STATUS "${preparation_output}")
    set(${output_variable} "${vim_source_dir}" PARENT_SCOPE)
endfunction()
