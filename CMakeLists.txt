cmake_minimum_required(VERSION 3.4 FATAL_ERROR)
project(project LANGUAGES CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin)
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
set(CMAKE_VERBOSE_MAKEFILE OFF)

find_package(Git REQUIRED)
find_package(PkgConfig REQUIRED)
find_package(Protobuf REQUIRED)
find_package(nlohmann_json 3.2.0 REQUIRED)

pkg_search_module(PROTOBUF REQUIRED protobuf)
pkg_search_module(CPPZMQ REQUIRED cppzmq)

if(NOT PROTOBUF_FOUND)
    message(FATAL_ERROR "PROTOBUF WAS NOT FOUND BY PKG-CONFIG.")
endif()

if(NOT CPPZMQ_FOUND)
    message(FATAL_ERROR "CPPZMQ WAS NOT FOUND BY PKG-CONFIG.")
endif()

# include(dpdk)
# include(iouring)
# include(proto)
# include(debug)

set(DEBUG_FLAGS "-g")
set(OPT_FLAGS "-O0")
set(WARN_FLAGS "-Wall")
set(GCC_COMPILE_FLAGS   "${DEBUG_FLAGS} ${OPT_FLAGS} ${WARN_FLAGS}")
set(CMAKE_CXX_FLAGS     ${CMAKE_CXX_FLAGS} ${GCC_COMPILE_FLAGS})

file(GLOB SOURCES           "src/utils/*.cpp")
set(PROJECT_SOURCES         ${SOURCES} ${PROTO_SRCS} ${PROTO_HDRS})
set(PROJECT_INCLUDES        ${PROJECT_SOURCE_DIR}/src ${PROJECT_SOURCE_DIR}/src/utils ${CPPZMQ_INCLUDE_DIRS} ${PROTOBUF_INCLUDE_DIRS} )
set(PROJECT_LIBRARIES       ${CPPZMQ_LIBRARIES} ${PROTOBUF_LIBRARIES})

set(PARENT "parent")
set(CHILD  "child")
set(MCAST  "mcast")
set(LEMON  "lemon")

include_directories(${PROJECT_INCLUDES})
add_executable(${PARENT} "${PROJECT_SOURCE_DIR}/src/parent.cpp" ${PROJECT_SOURCES})
target_compile_definitions(${PARENT} PUBLIC ZMQ_BUILD_DRAFT_API=1)
target_link_libraries(${PARENT} PUBLIC ${PROJECT_LIBRARIES})

include_directories(${PROJECT_INCLUDES})
add_executable(${CHILD} "${PROJECT_SOURCE_DIR}/src/child.cpp" ${PROJECT_SOURCES})
target_compile_definitions(${CHILD} PUBLIC ZMQ_BUILD_DRAFT_API=1)
target_link_libraries(${CHILD} PUBLIC ${PROJECT_LIBRARIES})

include_directories(${PROJECT_INCLUDES})
add_executable(${MCAST} "${PROJECT_SOURCE_DIR}/src/mcast.cpp" ${PROJECT_SOURCES})
target_compile_definitions(${MCAST} PUBLIC ZMQ_BUILD_DRAFT_API=1)
target_link_libraries(${MCAST} PUBLIC ${PROJECT_LIBRARIES})

include_directories(${PROJECT_INCLUDES})
add_executable(${LEMON} "${PROJECT_SOURCE_DIR}/src/lemon.cpp" ${PROJECT_SOURCES})
target_compile_definitions(${LEMON} PUBLIC ZMQ_BUILD_DRAFT_API=1)
target_link_libraries(${LEMON} PUBLIC ${PROJECT_LIBRARIES} nlohmann_json::nlohmann_json)

set_property(DIRECTORY PROPERTY ADDITIONAL_CLEAN_FILES
    "${PROJECT_SOURCE_DIR}/build/CMakeFiles"
    "${PROJECT_SOURCE_DIR}/build/CMakeCache.txt"
    "${PROJECT_SOURCE_DIR}/build/Makefile"
    "${PROJECT_SOURCE_DIR}/build/cmake_install.cmake"
    "${PROJECT_SOURCE_DIR}/build/lib"
    # "${PROJECT_SOURCE_DIR}/build/compile_commands.json"
)
