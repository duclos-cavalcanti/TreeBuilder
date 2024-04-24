PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

ifeq (, $(shell which packer))
$(error packer not found)
endif

ifeq (, $(shell which docker))
$(error docker not found)
endif

ifeq (, $(shell which vagrant))
$(error vagrant not found)
endif

ifeq (, $(shell which terraform))
$(error terraform not found)
endif

.PHONY: docker vagrant clean
all:

docker:
	@./run.sh --build docker
	@./run.sh --deploy docker

vagrant:
	@./run.sh --build  vagrant
	@./run.sh --deploy vagrant

clean:
	@./run.sh --clean
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}
	

