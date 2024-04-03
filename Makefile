SHELL := /bin/bash

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

all: build

.PHONY: help
help:
	echo help

.PHONY: jasper
jasper:
	@$(MAKE) -C tools/docker

.PHONY: freeze
freeze:
	pip freeze > requirements.txt

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: create
create:
	python3 -m venv .venv
	echo "source ./venv/bin/activate"

.PHONY: venv
venv: create install
	pip freeze > requirements.txt

.PHONY: docs
docs:
	@$(MAKE) -C docs

.PHONY: clean
clean:
	@echo clean
