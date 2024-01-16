SHELL := /bin/bash

all: build

.PHONY: build update clean

build:
	@printf 'build\n'

submodule:
	@git add dom-tenant-service
	@git commit -m "Updated submodule"
	@git push origin main

update:
	git submodule update --recursive

clean:
	@printf 'clean\n'
