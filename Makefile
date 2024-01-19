SHELL := /bin/bash

all: build

.PHONY: build update template pkg deploy delete package clean

build:
	@printf 'build\n'

update:
	@git add dom-tenant-service
	@git commit -m "Updated submodule"
	@git push origin main

template: templates/instance.yaml
	@python3 main.py template

pkg:
	@python3 main.py package

deploy: template pkg
	@python3 main.py deploy

delete:
	@python3 main.py delete

clean:
	@printf 'clean\n'
