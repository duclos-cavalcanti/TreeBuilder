ifeq (, $(shell which packer))
$(error packer not found)
endif

ifeq (, $(shell which docker))
$(error docker not found)
endif

ifeq (, $(shell which vagrant))
$(error vagrant not found)
endif

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

DOCKER := $(shell docker images -q ubuntu-base:jammy)

.PHONY: docker docker-build vagrant vagrant-build clean
all:

docker-build:
	packer build -var-file=./variables.pkr.hcl docker.pkr.hcl

docker: $(if ${DOCKER} , , docker-build)
	$(info Docker built.)

vagrant-build:
	packer build vbox.pkr.hcl

vagrant:
	$(info Vbox built.)

clean:

