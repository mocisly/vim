if(NOT VIM_ENABLE_QT_HOST)
    return()
endif()

# Match the C++ and Qt toolchain used by WetWeather without changing how the
# existing Vim C sources and Win32 GUI are compiled.
if(CMAKE_VERSION VERSION_LESS 4.2)
    message(FATAL_ERROR "The Vim Qt host requires CMake 4.2 or newer")
endif()
if(NOT MSVC OR CMAKE_CXX_COMPILER_VERSION VERSION_LESS 19.50)
    message(FATAL_ERROR "The Vim Qt host requires the VS2026 MSVC toolset (19.50 or newer)")
endif()
if(NOT CMAKE_CXX_STANDARD_LATEST)
    message(FATAL_ERROR "The Vim Qt host requires a compiler with CMake's latest C++ standard mode")
endif()

find_package(Qt6 6.12 REQUIRED COMPONENTS Core Gui Widgets)
find_program(VIM_QT_WINDEPLOYQT
    NAMES windeployqt windeployqt6
    HINTS "${Qt6_DIR}/../../../bin"
    NO_DEFAULT_PATH REQUIRED
)

set(VIM_QT_CXX_STANDARD "${CMAKE_CXX_STANDARD_LATEST}")
set(CMAKE_CXX${VIM_QT_CXX_STANDARD}_STANDARD_COMPILE_OPTION "-std:c++latest")
set(CMAKE_CXX${VIM_QT_CXX_STANDARD}_EXTENSION_COMPILE_OPTION "-std:c++latest")

add_library(vim_qt_host_config INTERFACE)
target_compile_features(vim_qt_host_config INTERFACE cxx_std_${VIM_QT_CXX_STANDARD})
target_compile_options(vim_qt_host_config INTERFACE
    $<$<COMPILE_LANGUAGE:CXX>:/W4>
    $<$<COMPILE_LANGUAGE:CXX>:/permissive->
    $<$<COMPILE_LANGUAGE:CXX>:/utf-8>
)
target_link_libraries(vim_qt_host_config INTERFACE
    Qt6::Core Qt6::Gui Qt6::Widgets
)

function(vim_configure_qt_host target_name)
    if(NOT TARGET ${target_name})
        message(FATAL_ERROR "Unknown Vim Qt host target: ${target_name}")
    endif()

    set_target_properties(${target_name} PROPERTIES
        CXX_STANDARD "${VIM_QT_CXX_STANDARD}"
        CXX_STANDARD_REQUIRED ON
        CXX_EXTENSIONS OFF
        CXX_SCAN_FOR_MODULES ON
        AUTOMOC ON
        AUTORCC ON
    )
    target_link_libraries(${target_name} PRIVATE vim_qt_host_config)
    add_custom_command(TARGET ${target_name} POST_BUILD
        COMMAND "${VIM_QT_WINDEPLOYQT}"
            "$<IF:$<CONFIG:Debug>,--debug,--release>"
            --no-translations --no-compiler-runtime
            "$<TARGET_FILE:${target_name}>"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${VIM_INTEGRATION_ROOT}/tests/fixtures/runtime_python_probe.py"
            "$<TARGET_FILE_DIR:${target_name}>/runtime_python_probe.py"
        VERBATIM
        COMMENT "Deploy Qt runtime for ${target_name}"
    )
endfunction()
