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

.PHONY: manager worker docker vagrant clean
all:

proto:
	cd manager && protoc --python_out . message.proto

manager:
	python3 main.py -m manager -a manager -i localhost -p 9090

worker:
	python3 main.py -m manager -a worker -i localhost -p 9090

docker:
	@./run.sh --build docker
	@./run.sh --deploy docker

vagrant:
	@./run.sh --build  vagrant
	@./run.sh --deploy vagrant

gcp:
	@./run.sh --deploy gcp

clean:
	@./run.sh --clean
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}
	

