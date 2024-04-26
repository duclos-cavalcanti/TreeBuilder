#!/bin/bash -e

usage() {
    echo "${0} [-h|--help] [-r|--remove <infra>] [-b|--build <infra>] [-d|--deploy <infra>] [-c|--clean <infra>]"
    echo "infra: {docker, vagrant, gcp}"
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
    pushd $terradir
        for d in "vagrant" "docker" "gcp"; do 
            pushd ${d}
                if [ -d ".terraform" ]; then 
                    if [ -n "$(terraform state list)" ]; then 
                        terraform destroy -auto-approve
                    fi
                fi
            popd
        done
    popd
    exit 0
}

deploy() {
    local infra="$1"
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
        terraform apply -auto-approve -var pwd=$(pwd)
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
    else 
        echo "Unsupported infrastructure: ${infra}"
        usage 
        exit 1
    fi
    
    pushd $packerdir
	packer build -var-file=./variables.pkr.hcl ${infra}.pkr.hcl
    popd
    exit 0
}

main() {
    while true; do
    case "$1" in
        -h | --help)
            usage 
            exit 0
            ;;

        -b | --build)
            arg="$2"
            shift 2
            build ${arg}
            break
            ;;

        -r | --remove)
            arg="$2"
            shift 2
            remove ${arg}
            break
            ;;

        -c | --clean)
            clean
            break
            ;;

        -d | --deploy)
            arg="$2"
            shift 2
            deploy ${arg}
            break
            ;;
        *)
            usage 
            exit 1
            ;;
    esac
    done
}

main $@
