cmake_minimum_required(VERSION 3.16.0 FATAL_ERROR)

project(vim_runtime C CXX)

set(VIM_INTEGRATION_ROOT "${CMAKE_CURRENT_SOURCE_DIR}")
set(VIM_UPSTREAM_SOURCE_DIR "${VIM_INTEGRATION_ROOT}/upstream/vim")

option(VIM_BUILD_SHARED_CORE "Build the Windows Vim runtime DLL" OFF)
option(VIM_ENABLE_QT_HOST "Configure the C++/Qt host for the embeddable Vim runtime" OFF)

include("${VIM_INTEGRATION_ROOT}/cmake/VimQtHost.cmake")
include("${VIM_INTEGRATION_ROOT}/cmake/VimSource.cmake")

vim_prepare_source(VIM_PATCHED_SOURCE_DIR)
add_subdirectory("${VIM_PATCHED_SOURCE_DIR}" "${CMAKE_BINARY_DIR}/vim-build")
