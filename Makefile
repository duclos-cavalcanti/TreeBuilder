SHELL := /bin/bash

all: build

.PHONY: build update clean

build:
	@printf 'build\n'

update:
	git submodule update

clean:
	@printf 'clean\n'
