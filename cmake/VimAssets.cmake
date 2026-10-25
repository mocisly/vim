foreach(config IN LISTS CMAKE_CONFIGURATION_TYPES)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}"
            "${VIM_INTEGRATION_ROOT}/tools/sync_vim_assets.py"
            --source "${CMAKE_CURRENT_SOURCE_DIR}"
            --extras "${VIM_INTEGRATION_ROOT}/assets/vim"
            --build-root "${CMAKE_BINARY_DIR}"
            --configuration "${config}"
        RESULT_VARIABLE assets_status
        OUTPUT_VARIABLE assets_output
        ERROR_VARIABLE assets_error
    )
    if(NOT assets_status EQUAL 0)
        message(FATAL_ERROR "Cannot sync Vim ${config} runtime files:\n${assets_error}")
    endif()
    string(STRIP "${assets_output}" assets_output)
    message(STATUS "${assets_output}")
endforeach()
