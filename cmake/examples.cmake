set(EXAMPLES_DIR ${PROJECT_SOURCE_DIR}/examples)
file(GLOB DIRS RELATIVE ${EXAMPLES_DIR} ${EXAMPLES_DIR}/*)

foreach(NAME IN LISTS DIRS)
    if(IS_DIRECTORY ${EXAMPLES_DIR}/${NAME})
        add_subdirectory("${EXAMPLES_DIR}/${NAME}/")
    endif()
endforeach()
