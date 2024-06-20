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

.PHONY: proto build udp mcast docker pull process clean rm docs test 
all: build

proto:
	cd manager/message && protoc --python_out . message.proto

build:
	@cd build && cmake ..
	@cd build && make

udp: build
	@python3 -m deploy -a plan -i docker -m udp -s 6
	@python3 -m deploy -a deploy -i docker

mcast: build
	@python3 -m deploy -a plan -i docker -m mcast -s 6 -f 2 -d 2
	@python3 -m deploy -a deploy -i docker

docker:
	@python3 -m deploy -a plan -i docker -s 20 -p 9092 -r 1000 -t 5 -d 3
	@python3 -m deploy -a deploy -i docker

pull:
	@sudo chown duclos:duclos -R infra/terra/docker/modules/default/volume
	@python3 -m analysis -a pull -i docker

process:
	@python3 -m analysis -a process -i docker
	@cd analysis/data && feh -r

clean:
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}
	@python3 -m deploy -a destroy -i docker

rm:
	@sudo rm -f infra/terra/docker/modules/default/volume/*.log
	@sudo rm -f infra/terra/docker/modules/default/volume/*.json
	@sudo rm -f infra/terra/docker/modules/default/volume/*.csv
	@sudo rm -rf infra/terra/docker/modules/default/volume/treefinder*

docs:
	$(MAKE) -C docs/slidev

test:
	@python3 -m pytest -v test/ -s
