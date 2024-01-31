cmake_minimum_required(VERSION 3.4 FATAL_ERROR)

project(project)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

find_package(PkgConfig REQUIRED)
include(dpdk)
include(iouring)

set(DEBUG_FLAGS "-g")
set(OPT_FLAGS "-O0")
set(WARN_FLAGS "-Wall")
set(GCC_COMPILE_FLAGS "${DEBUG_FLAGS} ${OPT_FLAGS} ${WARN_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${GCC_COMPILE_FLAGS}")

file(GLOB SOURCES "src/*.c")
set(PROJECT_SOURCES ${SOURCES})

set(PROJECT_INCLUDES 
    ${PROJECT_SOURCE_DIR}/include/ 
    ${DPDK_INCLUDE_DIRS} 
    ${LIBURING_INCLUDE_DIRS}
    )

include_directories(${PROJECT_INCLUDES})
add_executable(${PROJECT_NAME} ${PROJECT_SOURCES})
target_link_directories(${PROJECT_NAME} PRIVATE ${DPDK_LIBRARY_DIRS} ${LIBURING_LIBRARY_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${DPDK_LIBRARIES}${LIBURING_LIBRARIES})

set_property(DIRECTORY PROPERTY ADDITIONAL_CLEAN_FILES
    "${PROJECT_SOURCE_DIR}/build/CMakeFiles"
    "${PROJECT_SOURCE_DIR}/build/CMakeCache.txt"
    "${PROJECT_SOURCE_DIR}/build/Makefile"
    "${PROJECT_SOURCE_DIR}/build/cmake_install.cmake"
    "${PROJECT_SOURCE_DIR}/build/lib"
    # "${PROJECT_SOURCE_DIR}/build/compile_commands.json"
)

add_custom_target("run"
    COMMENT "Running Program"
    DEPENDS ${PROJECT_NAME}
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMAND ./bin/${PROJECT_NAME}
)

add_custom_target("debug"
    COMMENT "Debugging with GDB"
    DEPENDS ${PROJECT_NAME}
    WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    COMMAND gdb -tui -x ./GDBCOMMANDS --args ./bin/${PROJECT_NAME}
)
