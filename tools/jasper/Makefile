SHELL := /bin/bash

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

all: run

.PHONY: help
help:
	echo help

.PHONY: build
build:
	docker build -t ubuntu-dpdk ./tools/docker/

.PHONY: run
run: build
	docker run --rm \
	--name dpdk-dev \
	-v ${PWD}:/root/work \
	-v ~/.config/nvim:/root/.config/nvim \
	-v ~/.local/nvim:/root/.local/nvim \
	-v ~/.gitconfig:/root/.gitconfig \
	--detach-keys="ctrl-@" \
	-it ubuntu-dpdk
