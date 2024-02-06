set(EXAMPLES_DIR ${PROJECT_SOURCE_DIR}/examples)
set(ALL_EXAMPLE_TARGETS "")

file(GLOB DIRS RELATIVE ${EXAMPLES_DIR} ${EXAMPLES_DIR}/*)
foreach(NAME IN LISTS DIRS)
    if(IS_DIRECTORY ${EXAMPLES_DIR}/${NAME})
        file(GLOB SOURCES "${EXAMPLES_DIR}/${NAME}/*.c")

        if(SOURCES STREQUAL "")
            file(GLOB SOURCES "${EXAMPLES_DIR}/${NAME}/*.cpp")
        endif()

        if(SOURCES STREQUAL "")
            message(FATAL_ERROR "No C or C++ source files found: ${EXAMPLES_DIR}/${NAME}")
        endif()

        set(EXAMPLE_TARGET "example_${NAME}")
        set(EXAMPLE_SOURCES ${SOURCES})
        set(EXAMPLE_INCLUDES "${EXAMPLES_DIR}/${NAME}/" ${DPDK_INCLUDE_DIRS} ${LIBURING_INCLUDE_DIRS})

        add_executable(${EXAMPLE_TARGET} EXCLUDE_FROM_ALL ${EXAMPLE_SOURCES})
        include_directories(${EXAMPLE_INCLUDES})
        target_link_libraries(${EXAMPLE_TARGET} PRIVATE ${DPDK_LIBRARIES} ${LIBURING_LIBRARIES})
        target_include_directories(${EXAMPLE_TARGET} PRIVATE ${DPDK_INCLUDE_DIRS} ${LIBURING_INCLUDE_DIRS})

        list(APPEND ALL_EXAMPLE_TARGETS ${EXAMPLE_TARGET})
    endif()
endforeach()

add_custom_target(examples DEPENDS ${ALL_EXAMPLE_TARGETS})
message(STATUS "examples: ${ALL_EXAMPLE_TARGETS}")
