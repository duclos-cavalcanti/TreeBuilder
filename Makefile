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

.PHONY: proto udp docker vagrant gcp image clean rm
all:

proto:
	cd manager && protoc --python_out . message.proto
	cd src/utils && protoc --cpp_out . message.proto

udp:
	@./run.sh --build docker
	@./run.sh --deploy docker --mode udp

docker:
	@./run.sh --build docker
	@./run.sh --deploy docker

vagrant:
	@./run.sh --build  vagrant
	@./run.sh --deploy vagrant

image:
	@./run.sh --build gcp

gcp:
	@./run.sh --deploy gcp --mode default

clean:
	@./run.sh --clean
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}
	
rm: clean
	@./run.sh --remove docker
	

