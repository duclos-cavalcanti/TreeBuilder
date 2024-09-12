SHELL := /bin/bash
PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

TEXS := $(wildcard *.tex)
PDFS := $(TEXS:.tex=.pdf)

ifeq (, $(shell which docker))
$(error Docker not found)
endif

DOCKER := thomasweise/docker-texlive-full
NAME := latex-ma

.PHONY: exit \
		clean \
		build

all: build

exit:
	$(error Exiting Makefile)

clean:
	@rm -fv ./assets/*.aux 
	@rm -fv ./assets/*.bcf 
	@rm -fv ./assets/*.log 
	@rm -fv ./assets/*.lof
	@rm -fv ./assets/*.lot
	@rm -fv ./assets/*.xml 
	@rm -fv ./assets/*.xmpi 

pull:
	@docker pull ${DOCKER}

build: ThesisLKN.pdf

%.pdf: %.tex
	$(info TEX: $< => PDF: $@)	
	@docker run --rm \
			   --user $(UID):$(GID) \
			   --name ${NAME} \
			   -v ${PWD}:/data \
			   -w /data \
			   ${DOCKER}:latest \
			   pdflatex $<; bibtex $*; pdflatex $<
	@mv $@ assets/
