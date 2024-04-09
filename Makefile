PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

DOCKER := ubuntu-ma

ifeq (, $(shell which docker))
$(error Docker not found)
endif

ifeq (, $(shell which packer))
$(error Packer not found)
endif

all: build

.PHONY: help
help:
	echo help

.PHONY: freeze
freeze:
	pip freeze > requirements.txt

.PHONY: install
install:
	pip install -r requirements.txt
	@# python3 -m pip install 'requests==2.18.4'

.PHONY: venv
venv:
	python3 -m venv .venv
	echo "source ./venv/bin/activate"

.PHONY: pack
pack:
	python3 main.py -m deploy -a build -i packer

.PHONY: rmi
rmi:
	@docker rmi $(shell docker images ${DOCKER} --format "{{.ID}}")

.PHONY: docker
docker: $(if $(shell docker images --format "{{.Repository}}" | grep ${DOCKER}), , pack)

.PHONY: jasper
jasper:
	@$(MAKE) -C tools/docker

.PHONY: docs
docs:
	@$(MAKE) -C docs

.PHONY: clean
clean:
	@echo clean
