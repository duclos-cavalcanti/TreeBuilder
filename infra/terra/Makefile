ifeq (, $(shell which terraform))
$(error Terraform not found)
endif

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

DOCKER := $(shell docker images -q ubuntu-base:jammy)

.PHONY: docker docker-build clean
all:

docker-build:
	cd docker && terraform init
	cd docker && terraform apply -auto-approve -var pwd=${PWD}/docker

docker: $(if ${DOCKER} , , docker-build)

clean:
	cd docker && terraform destroy -auto-approve

