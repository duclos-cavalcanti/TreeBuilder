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
NAME := latex-resume

.PHONY: exit \
		clean \
		build

all: build

exit:
	$(error Exiting Makefile)

clean:
	@rm -v ./assets/*.aux 
	@rm -v ./assets/*.bcf 
	@rm -v ./assets/*.log 
	@rm -v ./assets/*.xml 
	@rm -v ./assets/*.xmpi 

pull:
	@docker pull ${DOCKER}

build: ${PDFS}

slides:
	$(MAKE) -C slidev

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
