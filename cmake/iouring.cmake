include(ExternalProject)
set(IOURING_INSTALL_DIR "${PROJECT_SOURCE_DIR}/lib/iouring")

ExternalProject_Add(iouring
    GIT_REPOSITORY https://github.com/axboe/liburing.git
    GIT_TAG master
    CONFIGURE_COMMAND ./configure --prefix=${IOURING_INSTALL_DIR} --cc=gcc --cxx=g++
    BUILD_COMMAND make
    INSTALL_COMMAND make install
    BUILD_IN_SOURCE TRUE
    LOG_DOWNLOAD ON
    LOG_BUILD ON
    LOG_INSTALL ON
)

set(ENV{PKG_CONFIG_PATH} "${LIBURING_INSTALL_DIR}/lib/pkgconfig:$ENV{PKG_CONFIG_PATH}")
pkg_check_modules(LIBURING REQUIRED liburing)
