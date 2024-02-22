include(ExternalProject)
set(ZEROMQ_INSTALL_DIR ${PROJECT_SOURCE_DIR}/lib/zeromq)

ExternalProject_Add(zeroMQ
    GIT_REPOSITORY https://github.com/zeromq/libzmq.git
    GIT_TAG master
    CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${ZEROMQ_INSTALL_DIR}
        -DWITH_PERF_TOOL=OFF
        -DZMQ_BUILD_TESTS=OFF
        -DENABLE_CPACK=OFF
        -DBUILD_SHARED_LIBS=ON 
        -DENABLE_DRAFTS=ON
    INSTALL_DIR ${ZEROMQ_INSTALL_DIR}
)

set(CPPZMQ_INSTALL_DIR ${PROJECT_SOURCE_DIR}/lib/cppzmq)
ExternalProject_Add(cppzmq
    DEPENDS zeroMQ
    GIT_REPOSITORY https://github.com/zeromq/cppzmq.git
    GIT_TAG master
    CMAKE_ARGS
        -DCMAKE_INSTALL_PREFIX=${CPPZMQ_INSTALL_DIR}
        -DZeroMQ_DIR=${ZEROMQ_INSTALL_DIR}/lib/cmake/ZeroMQ
        -DBUILD_SHARED_LIBS=ON 
    INSTALL_DIR ${CPPZMQ_INSTALL_DIR}
)

set(ENV{PKG_CONFIG_PATH} "${ZEROMQ_INSTALL_DIR}/lib/pkgconfig:${CPPZMQ_INSTALL_DIR}/lib/pkgconfig")
pkg_check_modules(CPPZMQ QUIET IMPORTED_TARGET cppzmq)
