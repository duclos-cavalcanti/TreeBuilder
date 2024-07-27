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

PREFIX  := 2024-07-21-15-07-42
GPREFIX := 2024-07-21-13-08-04

.PHONY: proto build udp mcast docker pull process clean rm docs test 
all: build

proto:
	cd manager/message && protoc --python_out . message.proto

build:
	@cd build && cmake ..
	@cd build && make

udp:
	@python3 -m deploy -a plan -i docker -m udp -s 8
	@python3 -m deploy -a deploy -i docker

mcast:
	@python3 -m deploy -a plan -i docker -m mcast -s 6 -f 2 -d 2
	@python3 -m deploy -a deploy -i docker

lemon:
	@python3 -m deploy -a plan -i docker -m lemon -s 3 -t 15
	@python3 -m deploy -a deploy -i docker

image:
	@python3 -m deploy -a build -i docker

lemondrop:
	@python3 -m deploy -a plan -i docker -m lemondrop -s 20 -d 3 -f 2 -p 9092 -n 1
	@python3 -m deploy -a deploy -i docker

docker:
	@python3 -m deploy -a plan -i docker -s 20 -p 9092 -r 5000 -t 10 -e 30 -d 3 -f 2 -n 3 -c 2
	@python3 -m deploy -a deploy -i docker

pull:
	@sudo chown duclos:duclos -R infra/terra/docker/modules/default/volume
	python3 -m analysis -a pull -i docker -p ${PREFIX}

process:
	python3 -m analysis -a process -i docker -v yes -p ${PREFIX}
	@#python3 -m analysis -a process -i docker -m udp

super:
	@python3 -m analysis -a process -i gcp -m super -p ${GPREFIX}

destroy:
	@python3 -m deploy -a destroy -i docker

gimage:
	@python3 -m deploy -a build -i gcp

gcp:
	@python3 -m deploy -a plan -i gcp -s 25 -p 9092 -r 5000 -t 20 -d 3 -f 2 -n 3
	@python3 -m deploy -a deploy -i gcp

gpull:
	python3 -m analysis -a pull -i gcp -p ${GPREFIX}

gprocess:
	python3 -m analysis -a process -i gcp -v yes -p ${GPREFIX}

gcopy:
	python3 -m analysis -a generate -i gcp -p ${GPREFIX}

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
	$(MAKE) -C docs slides

test:
	@python3 -m pytest -v test/ -k LemonDrop -s
