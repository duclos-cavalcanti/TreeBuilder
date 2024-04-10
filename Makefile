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

ifeq (, $(shell which terraform))
$(error Terraform not found)
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

compress:
	@tar --exclude=jasper \
		 --exclude=project.tar.gz \
		 --exclude=.git \
		 --exclude=.gitkeep \
		 --exclude=.gitignore \
		 --exclude=.gitmodules \
		 --exclude=examples \
		 --exclude=lib \
		 --exclude=.cache \
		 --exclude=deploy \
		 --exclude=analysis \
		 --exclude-vcs-ignores \
		 -P build \
		 -zcvf ./project.tar.gz .

.PHONY: build
build:
	python3 main.py -m deploy -a build -i docker

.PHONY: rm
rm:
	@$(if $(shell docker images --format "{{.Repository}}" | grep ${DOCKER}), docker rmi $(shell docker images ${DOCKER} --format "{{.ID}}"), $(info Nothing to be done.))
	
.PHONY: docker
docker: compress $(if $(shell docker images --format "{{.Repository}}" | grep ${DOCKER}), rm build, build)

.PHONY: jasper
jasper:
	@$(MAKE) -C tools/docker

.PHONY: docs
docs:
	@$(MAKE) -C docs

.PHONY: clean
clean:
	@echo clean
