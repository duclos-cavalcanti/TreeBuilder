SHELL := /bin/bash

all: build

.PHONY: build update clean

build:
	@printf 'build\n'

update-module:
	git submodule update --recursive

update:
	@git add dom-tenant-service
	@git commit -m "Updated submodule"
	@git push origin main

clean:
	@printf 'clean\n'
