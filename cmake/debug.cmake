if(DEV)
    message(WARNING "DPDK INCLUDES:"    ${DPDK_INCLUDE_DIRS})
    message(WARNING "DPDK LIBRARIES:n"  ${DPDK_LIBRARIES})
    message(WARNING "DPDK LDIRS:"       ${DPDK_LIBRARY_DIRS})
    message(WARNING "DPDK LDFLAGS:  "   ${DPDK_LDFLAGS})
    message(WARNING "URING INCLUDES:"   ${LIBURING_INCLUDE_DIRS})
    message(WARNING "URING LIBRARIES:n" ${LIBURING_LIBRARIES})
    message(WARNING "URING LDIRS:"      ${LIBURING_LIBRARY_DIRS})
    message(WARNING "URING LDFLAGS:  "  ${LIBURING_LDFLAGS})
    message(WARNING "URING LDIRS:"      ${LIBURING_LIBRARY_DIRS})
    message(WARNING "PROJECT INCLUDES:  "   ${PROJECT_INCLUDES})
    message(WARNING "PROJECT LIBRARIES:  "  ${PROJECT_LIBRARIES})
    message(WARNING "PROJECT CFLAGS:  "     ${CMAKE_C_FLAGS})
endif()
