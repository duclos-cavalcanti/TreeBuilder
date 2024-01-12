SHELL := /bin/bash

all: build

.PHONY: build update clean

build:
	@printf 'build\n'

update:
	git submodule update --recursive

clean:
	@printf 'clean\n'
