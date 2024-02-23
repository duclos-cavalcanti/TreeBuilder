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
	docker build -t ubuntu-dpdk ./tools/docker/

.PHONY: dev
dev:
	docker run --rm \
	--name dpdk-dev \
	-v ${PWD}:/root/work \
	-v ~/.config/nvim:/root/.config/nvim \
	-v ~/.local/nvim:/root/.local/nvim \
	-v ~/.gitconfig:/root/.gitconfig \
	--detach-keys="ctrl-@" \
	-it ubuntu-dpdk

.PHONY: update
update:
	@git add module
	@git commit -m "Updated submodule"
	@git push origin main

.PHONY: deploy
deploy:
	@python3 deploy/main.py

.PHONY: docs
delete:
	@$(MAKE) -C docs

.PHONY: clean
clean:
	@echo clean
