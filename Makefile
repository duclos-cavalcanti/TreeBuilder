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

PREFIX := 06-22-20:20:16

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
	@python3 -m deploy -a plan -i docker -s 20 -p 9092 -r 5000 -t 15 -d 3
	@python3 -m deploy -a deploy -i docker

pull:
	@sudo chown duclos:duclos -R infra/terra/docker/modules/default/volume
	python3 -m analysis -a pull -i docker -p ${PREFIX}

process:
	python3 -m analysis -a process -i docker -v yes -p ${PREFIX}

destroy:
	@python3 -m deploy -a destroy -i docker

gcp:
	@python3 -m deploy -a plan -i gcp -s 20 -p 9092 -r 5000 -t 20 -d 3
	@python3 -m deploy -a deploy -i gcp

gpull:
	python3 -m analysis -a pull -i gcp -p 06-22-22:19:00

gprocess:
	python3 -m analysis -a process -i gcp -v yes -p 06-22-22:19:00

gdestroy:
	@python3 -m deploy -a destroy -i gcp

clean:
	@find . -path ./jasper -prune -type f -name "*.tar.gz" -print0 | xargs -0 -I {} rm -v {}

rm:
	@sudo rm -vf infra/terra/docker/modules/default/volume/*.log
	@sudo rm -vf infra/terra/docker/modules/default/volume/*.json
	@sudo rm -vf infra/terra/docker/modules/default/volume/*.csv
	@sudo rm -vrf infra/terra/docker/modules/default/volume/treefinder*

docs:
	$(MAKE) -C docs/slidev

test:
	@python3 -m pytest -v test/ -s
