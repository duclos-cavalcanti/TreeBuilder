cmake_minimum_required(VERSION 3.4 FATAL_ERROR)
project(project LANGUAGES C CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_VERBOSE_MAKEFILE OFF)

find_package(Git REQUIRED)
find_package(PkgConfig REQUIRED)

include(dpdk)
include(iouring)

set(DEBUG_FLAGS "-g")
set(OPT_FLAGS "-O0")
set(WARN_FLAGS "-Wall")
set(GCC_COMPILE_FLAGS "${DEBUG_FLAGS} ${OPT_FLAGS} ${WARN_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${GCC_COMPILE_FLAGS} ${DPDK_CFLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${GCC_COMPILE_FLAGS}")

if(NOT DPDK_FOUND OR NOT LIBURING_FOUND)
    message(WARNING "DPDK AND LIBURING WERE NOT FOUND BY PKG-CONFIG.")
endif()


file(GLOB SOURCES "src/*.c")
set(PROJECT_SOURCES ${SOURCES})
set(PROJECT_INCLUDES ${PROJECT_SOURCE_DIR}/src/ ${DPDK_INCLUDE_DIRS} ${LIBURING_INCLUDE_DIRS})
set(PROJECT_LIBRARY_DIRS ${DPDK_LIBRARY_DIRS} ${LIBURING_LIBRARY_DIRS})
set(PROJECT_LIBRARIES ${DPDK_LINK_LIBRARIES} ${LIBURING_LINK_LIBRARIES})

include_directories(${PROJECT_INCLUDES})
add_executable(${PROJECT_NAME} ${PROJECT_SOURCES})
link_directories(${PROJECT_LIBRARIES} ${PROJECT_LIBRARY_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${PROJECT_LIBRARIES})

set_property(DIRECTORY PROPERTY ADDITIONAL_CLEAN_FILES
    "${PROJECT_SOURCE_DIR}/build/CMakeFiles"
    "${PROJECT_SOURCE_DIR}/build/CMakeCache.txt"
    "${PROJECT_SOURCE_DIR}/build/Makefile"
    "${PROJECT_SOURCE_DIR}/build/cmake_install.cmake"
    "${PROJECT_SOURCE_DIR}/build/lib"
    # "${PROJECT_SOURCE_DIR}/build/compile_commands.json"
)

add_custom_target("run"
    DEPENDS ${PROJECT_NAME}
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMAND ./bin/${PROJECT_NAME}
)

add_custom_target("debug"
    DEPENDS ${PROJECT_NAME}
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMAND gdb -tui -x ./GDBCOMMANDS --args ./bin/${PROJECT_NAME}
)

add_custom_target("reset"
    DEPENDS ${PROJECT_NAME}
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMAND rm -rf ./lib/dpdk/* ./lib/iouring/*
    COMMAND rm  -rf "${PROJECT_SOURCE_DIR}/build/dpdk-prefix"
    COMMAND rm  -rf "${PROJECT_SOURCE_DIR}/build/liburing-prefix"
)

include(debug)
include(examples)
