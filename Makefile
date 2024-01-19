SHELL := /bin/bash

all: help

.PHONY: build update template pkg deploy delete clean
.PHONY: scripts

help:
	echo help

build:
	@MAKE -C src

update:
	@git add dom-tenant-service
	@git commit -m "Updated submodule"
	@git push origin main

template:
	@python3 main.py template

scripts: $(wildcard scripts/*.sh)
	@python3 main.py scripts

pkg:
	@python3 main.py package

deploy: template pkg
	@python3 main.py deploy

delete:
	@python3 main.py delete

clean:
	@printf 'clean\n'
