include(ExternalProject)

set(LIBURING_INSTALL_DIR "${PROJECT_SOURCE_DIR}/lib/iouring")

ExternalProject_Add(liburing
    GIT_REPOSITORY https://github.com/axboe/liburing.git
    GIT_TAG master
    UPDATE_DISCONNECTED TRUE
    CONFIGURE_COMMAND ./configure --prefix=${LIBURING_INSTALL_DIR} --cc=gcc --cxx=g++
    BUILD_COMMAND make
    INSTALL_COMMAND make install
    BUILD_IN_SOURCE TRUE
    LOG_DOWNLOAD ON
    LOG_BUILD ON
    LOG_INSTALL ON
)
set(ENV{PKG_CONFIG_PATH} "${PROJECT_SOURCE_DIR}/lib/iouring/lib/pkgconfig:$ENV{PKG_CONFIG_PATH}")
pkg_search_module(LIBURING QUIET IMPORTED_TARGET liburing)
