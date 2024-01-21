SHELL := /bin/bash

all: template pkg deploy

.PHONY: help
help:
	echo help

.PHONY: build
build:
	@MAKE -C src

.PHONY: update
update:
	@git add dom-tenant-service
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
