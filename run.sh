#!/bin/bash -e

usage() {
    echo "${0} [-h|--help] [-r|--remove <infra>] [-b|--build <infra>] [-d|--deploy <infra>] [-c|--clean <infra>]"
    echo "infra: {docker, vagrant, gcp, test}"
}

compress() {
    local dst="${1}/project.tar.gz"
	tar --exclude=jasper \
		--exclude=project.tar.gz \
		--exclude=.git \
		--exclude=.gitkeep \
		--exclude=.gitignore \
		--exclude=.gitmodules \
		--exclude=examples \
		--exclude=lib \
		--exclude=build \
		--exclude=.cache \
		--exclude=terra \
		--exclude=infra \
		--exclude=analysis \
		--exclude-vcs-ignores \
		-zcvf ${dst} .
}

clean() {
    local terradir="infra/terra"
    pushd $terradir > /dev/null
        for d in "vagrant" "docker" "gcp"; do 
            pushd ${d} > /dev/null
            echo "CLEANING: ${d^^}"
                if [ -d ".terraform" ]; then 
                    if [ -n "$(terraform state list)" ]; then 
                        terraform destroy -auto-approve -var pwd=$(pwd)
                    fi
                fi
            popd > /dev/null
        done
    popd > /dev/null
    exit 0
}

deploy() {
    local infra="$1"
    local mode="$2"
    local terradir="infra/terra"
    local isdockerbuilt="$(docker images -q ubuntu-base:jammy)"
    local isvagrantbuilt="$(vagrant box list | grep ubuntu-base)"

    if [ "$infra" == "docker" ]; then 
        test -z "${isdockerbuilt}" && echo "Docker hasn't been built."   && exit 1
    elif [ "$infra" == "vagrant" ]; then 
        test -z "${isvagrantbuilt}" && echo "Vagrant hasn't been built." && exit 1
    elif [ "$infra" == "gcp" ]; then 
        echo ""
    else 
        echo "Unsupported infrastructure: ${infra}"
        usage 
        exit 1
    fi
    
    compress "$terradir/${infra}/extract"
    pushd $terradir/${infra}
        terraform init
        terraform apply -auto-approve -var pwd=$(pwd) -var mode=${mode}
    popd
    exit 0
}

remove() {
    local infra="$1"
    local packerdir="infra/packer"
    local isdockerbuilt="$(docker images -q ubuntu-base:jammy)"
    local isvagrantbuilt="$(vagrant box list | grep ubuntu-base)"

    if [ "$infra" == "docker" ]; then 
        test -z "${isdockerbuilt}" && echo "Docker hasn't been built." && exit 0
        docker rmi ubuntu-base:jammy
    elif [ "$infra" == "vagrant" ]; then 
        test -z "${isvagrantbuilt}" && echo "Vagrant hasn't been built." && exit 0
        vagrant box remove ubuntu-base
        test -d "${packerdir}/output-box" && rm -rf "${packerdir}/output-box"
    else 
        echo "Unsupported infrastructure: ${infra}"
        usage 
        exit 1
    fi
}

build() {
    local infra="$1"
    local packerdir="infra/packer/"
    local isdockerbuilt="$(docker images -q ubuntu-base:jammy)"
    local isvagrantbuilt="$(vagrant box list | grep ubuntu-base)"

    if [ "$infra" == "docker" ]; then 
        test -n "${isdockerbuilt}" && echo "Docker built." && exit 0
    elif [ "$infra" == "vagrant" ]; then 
        test -n "${isvagrantbuilt}" && echo "Vagrant built." && exit 0
    elif [ "$infra" == "gcp" ]; then 
        echo
    else 
        echo "Unsupported infrastructure: ${infra}"
        usage 
        exit 1
    fi
    
    pushd $packerdir
	packer build -force -var-file=./variables.pkr.hcl ${infra}.pkr.hcl
    popd
    exit 0
}

main() {
    action=""
    infra=""
    mode=""
    while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help)
            usage 
            exit 0
            ;;

        -m | --mode)
            mode="$2"
            shift 2
            ;;

        -b | --build)
            action="build"
            infra="$2"
            shift 2
            ;;

        -r | --remove)
            action="remove"
            infra="$2"
            shift 2
            ;;

        -c | --clean)
            action="clean"
            shift 1
            ;;

        -d | --deploy)
            action="deploy"
            infra="$2"
            shift 2
            ;;
        *)
            usage 
            exit 1
            ;;
    esac
    done

    echo "ACTION=$action INFRA=$infra MODE=$mode"
    $action $infra $mode
}

main $@
