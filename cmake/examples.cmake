set(EXAMPLES_DIR ${PROJECT_SOURCE_DIR}/examples)
set(ALL_EXAMPLE_TARGETS "")


file(GLOB DIRS RELATIVE ${EXAMPLES_DIR} ${EXAMPLES_DIR}/*)
foreach(NAME IN LISTS DIRS)
    if(IS_DIRECTORY ${EXAMPLES_DIR}/${NAME})
        file(GLOB SOURCES "${EXAMPLES_DIR}/${NAME}/*.c")

        set(EXAMPLE_TARGET          "x_${NAME}")
        set(EXAMPLE_SOURCES         "${SOURCES}")
        set(EXAMPLE_INCLUDES        "${EXAMPLES_DIR}/${NAME}/" "${LIBRARY_INCLUDES}")
        set(EXAMPLE_LIBRARIES       "${LIBRARIES}")

        if(SOURCES STREQUAL "")
            file(GLOB SOURCES "${EXAMPLES_DIR}/${NAME}/*.cpp")
            set(EXAMPLE_SOURCES         "${SOURCES}" "${PROTO_SRCS}" "${PROTO_HDRS}")
            set(EXAMPLE_INCLUDES        "${EXAMPLES_DIR}/${NAME}/" "${ZEROMQ_INCLUDE_DIRS}" "${CPPZMQ_INCLUDE_DIRS}" "${PROTOBUF_INCLUDE_DIRS}" "${CMAKE_CURRENT_BINARY_DIR}")
            set(EXAMPLE_LIBRARY_DIRS    "${CPPZMQ_LIBRARY_DIRS}")
            set(EXAMPLE_LIBRARIES       "${LIBZMQ_LINK_LIBRARIES}" "${PROTOBUF_LIBRARIES}")

            add_executable(${EXAMPLE_TARGET}                EXCLUDE_FROM_ALL ${EXAMPLE_SOURCES})
            target_compile_definitions(${EXAMPLE_TARGET}    PRIVATE ZMQ_BUILD_DRAFT_API=1)
            target_include_directories(${EXAMPLE_TARGET}    PRIVATE ${EXAMPLE_INCLUDES})
            target_link_directories(${EXAMPLE_TARGET}       PRIVATE ${EXAMPLE_LIBRARY_DIRS})
            target_link_libraries(${EXAMPLE_TARGET}         PRIVATE ${EXAMPLE_LIBRARIES})

            # message(STATUS "SRCS: ${EXAMPLE_SOURCES}")
            # message(STATUS "INCLUDE_DIRS: ${EXAMPLE_INCLUDES}")
            # message(STATUS "LINK_LIBRARIES: ${EXAMPLE_LIBRARIES}")
        else()
            add_executable(${EXAMPLE_TARGET}                EXCLUDE_FROM_ALL ${EXAMPLE_SOURCES})
            target_include_directories(${EXAMPLE_TARGET}    PRIVATE ${EXAMPLE_INCLUDES})
            target_link_libraries(${EXAMPLE_TARGET}         PRIVATE ${EXAMPLE_LIBRARIES})
        endif()

        list(APPEND ALL_EXAMPLE_TARGETS ${EXAMPLE_TARGET})
    endif()
endforeach()

add_custom_target(examples DEPENDS ${ALL_EXAMPLE_TARGETS})
# message(STATUS "EXAMPLES: ${ALL_EXAMPLE_TARGETS}")
