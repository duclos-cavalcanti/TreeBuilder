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

.PHONY: docs
docs:
	@$(MAKE) -C docs

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

.PHONY: proto
proto:
	protoc --python_out="./manager" src/proto/message.proto
	mv manager/src/proto/*.py manager
	rm -rf manager/src

.PHONY: bundle
bundle:
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
		 --exclude=terra \
		 --exclude=analysis \
		 --exclude-vcs-ignores \
		 -zcvf ./deploy/terra/docker/project.tar.gz .

.PHONY: build
build:
	@docker build . -t ubuntu-base:jammy

.PHONY: docker
docker: build bundle proto
	cd deploy/terra/docker/ && terraform init
	cd deploy/terra/docker/ && terraform apply -auto-approve

.PHONY: clean
clean:
	@cd deploy/terra/docker && terraform destroy -auto-approve

reset: 
	@docker rmi ubuntu-base:jammy
