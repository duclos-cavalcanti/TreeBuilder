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

.PHONY: build docs test proto udp docker vagrant gcp image clean rm
all: build

proto:
	cd manager/message && protoc --python_out . message.proto
	@#cd src/utils && protoc --cpp_out . message.proto

udp: build
	@./run.sh --build docker
	@./run.sh --deploy docker --mode udp

build:
	@cd build && cmake ..
	@cd build && make

docker:
	@./run.sh --build docker
	@./run.sh --deploy docker --mode manager

vagrant:
	@./run.sh --build  vagrant
	@./run.sh --deploy vagrant

gcp:
	@./run.sh --deploy gcp --mode default

image:
	@./run.sh --build gcp

clean:
	@./run.sh --clean
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}

rm: clean
	@./run.sh --remove docker

docs:
	$(MAKE) -C docs/slidev

test:
	@python3 -m pytest -v test/ -s
