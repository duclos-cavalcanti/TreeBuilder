PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

ifeq (, $(shell which docker))
$(error Docker not found)
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

.PHONY: zip
zip:
	@tar --exclude=jasper \
		 --exclude=project.tar.gz \
		 --exclude=.git \
		 --exclude=.gitkeep \
		 --exclude=.gitignore \
		 --exclude=.gitmodules \
		 --exclude=examples \
		 --exclude=lib \
		 --exclude=build \
		 --exclude=.cache \
		 --exclude=deploy \
		 --exclude=analysis \
		 --exclude-vcs-ignores \
		 -zcvf ./project.tar.gz .
	@cp ./project.tar.gz ./deploy/terra/docker

.PHONY: docker-base
docker-base:
	$(if $(shell docker images --format "{{.Repository}}" | grep ubuntu-ma-base), , docker build . -t ubuntu-ma-base:jammy)

.PHONY: docker-rm
docker-rm:
	$(if $(shell docker images --format "{{.Repository}}" | grep ubuntu-ma-instance), docker rmi $(shell docker images ubuntu-ma-instance --format "{{.ID}}"), )

.PHONY: docker-build
docker-build: docker-base
	$(if $(shell docker images --format "{{.Repository}}" | grep ubuntu-ma-instance), , docker build deploy/terra/docker -t ubuntu-ma-instance:jammy --build-arg BUNDLE=project.tar.gz)

.PHONY: docker
docker: zip docker-build
	python3 main.py -m deploy -a deploy -i docker

.PHONY: destroy
destroy:
	@cd deploy/terra/docker && terraform destroy -auto-approve

.PHONY: docs
docs:
	@$(MAKE) -C docs

.PHONY: clean
clean: destroy docker-rm

.PHONY: nuke
nuke: destroy docker-rm
	$(if $(shell docker images --format "{{.Repository}}" | grep ubuntu-ma-base), docker rmi $(shell docker images ubuntu-ma-base --format "{{.ID}}"), )
