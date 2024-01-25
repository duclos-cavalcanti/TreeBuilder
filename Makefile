SHELL := /bin/bash

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

all: build

.PHONY: help
help:
	echo help

.PHONY: build
build:
	docker build -t ubuntu-dpdk .

.PHONY: dev
dev:
	@docker run --rm \
	--name dpdk-dev \
	-v ${PWD}:/root/work \
	-v ~/.config/nvim:/root/.config/nvim \
	-v ~/.gitconfig:/root/.gitconfig \
	--detach-keys="ctrl-@" \
	-it ubuntu-dpdk

.PHONY: update
update:
	@git add module
	@git commit -m "Updated submodule"
	@git push origin main

.PHONY: template
template:
	@python3 main.py template

.PHONY: pkg
pkg:
	@python3 main.py package

.PHONY: deploy
deploy:
	@python3 main.py deploy

.PHONY: delete
delete:
	@python3 main.py delete

.PHONY: clean
clean:
	@echo clean
