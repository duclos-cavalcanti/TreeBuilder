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

build:
	@cd build && cmake ..
	@cd build && make

udp: build
	@./run.sh --deploy docker --mode udp

mcast: build
	@./run.sh --deploy docker --mode mcast

docker:
	@./run.sh --build docker
	@./run.sh --deploy docker --mode manager --yaml "./plans/docker.yaml"

clean:
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}

docs:
	$(MAKE) -C docs/slidev

test:
	@python3 -m pytest -v test/ -s
