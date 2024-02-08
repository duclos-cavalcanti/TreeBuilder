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
            set(EXAMPLE_SOURCES         "${SOURCES}")
            set(EXAMPLE_INCLUDES        "${EXAMPLES_DIR}/${NAME}/" "${LIBRARY_INCLUDES}" "${ZEROMQ_INCLUDE_DIR}")
            set(EXAMPLE_LIBRARIES       "${LIBRARIES}" "${ZEROMQ_LINK_LIBRARIES}")
        endif()

        if(SOURCES STREQUAL "")
            message(FATAL_ERROR "No C or C++ source files found: ${EXAMPLES_DIR}/${NAME}")
        endif()

        add_executable(${EXAMPLE_TARGET}                EXCLUDE_FROM_ALL ${EXAMPLE_SOURCES})
        target_include_directories(${EXAMPLE_TARGET}    PRIVATE ${EXAMPLE_INCLUDES})
        target_link_libraries(${EXAMPLE_TARGET}         PRIVATE ${EXAMPLE_LIBRARIES})

        list(APPEND ALL_EXAMPLE_TARGETS ${EXAMPLE_TARGET})
    endif()
endforeach()

add_custom_target(examples DEPENDS ${ALL_EXAMPLE_TARGETS})
message(STATUS "EXAMPLES: ${ALL_EXAMPLE_TARGETS}")
