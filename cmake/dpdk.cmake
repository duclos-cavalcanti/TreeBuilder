include(ExternalProject)
set(DPDK_VERSION "23.07")
set(DPDK_INSTALL_DIR "${PROJECT_SOURCE_DIR}/lib/dpdk")

ExternalProject_Add(dpdk
    PREFIX ${DPDK_INSTALL_DIR}
    URL "https://fast.dpdk.org/rel/dpdk-${DPDK_VERSION}.tar.xz"
    CONFIGURE_COMMAND ""
    BUILD_IN_SOURCE TRUE
    BUILD_COMMAND meson setup -Dexamples=all -Dprefix=${DPDK_INSTALL_DIR} build
    INSTALL_COMMAND ninja -C build install
    LOG_DOWNLOAD ON
    LOG_BUILD ON
    LOG_INSTALL ON
)

set(ENV{PKG_CONFIG_PATH} "${DPDK_INSTALL_DIR}/lib/x86_64-linux-gnu/pkgconfig:$ENV{PKG_CONFIG_PATH}")
pkg_check_modules(DPDK REQUIRED libdpdk)

