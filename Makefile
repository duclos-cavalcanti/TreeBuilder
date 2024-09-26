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

PREFIX  := 2024-08-01-22-23-52
GPREFIX := 2024-08-04-13-01-35

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

lemondrop:
	@python3 -m deploy -a plan -i docker -m lemondrop -s 20 -d 3 -f 2 -p 9092 -n 1
	@python3 -m deploy -a deploy -i docker

docker:
	@python3 -m deploy -a build -i docker

local:
	@python3 -m deploy -a plan -i docker -s 14 -p 9092 -r 5000 -t 5 -w 2 -e 10 -d 2 -f 2 -n 1 -c 1 -b 1
	@python3 -m deploy -a deploy -i docker

pull:
	@sudo chown duclos:duclos -R infra/terra/docker/modules/default/volume
	python3 -m analysis -a pull -i docker -p ${PREFIX}

process:
	@python3 -m analysis -a process -i docker -s yes -p ${PREFIX}

destroy:
	@python3 -m deploy -a destroy -i docker

image:
	@python3 -m deploy -a build -i gcp

instance:
	@python3 -m deploy -a plan -i gcp -m test
	@python3 -m deploy -a deploy -i gcp

gcp:
	@python3 -m deploy -a plan -i gcp -s 25 -p 9092 -r 10000 -t 10 -w 2 -e 30 -d 3 -f 2 -n 1 -c 3 -b 2
	@python3 -m deploy -a deploy -i gcp

gpull:
	@python3 -m analysis -a pull -i gcp -p ${GPREFIX}

gprocess:
	@python3 -m analysis -a process -i gcp -m default -p ${GPREFIX}

super:
	@python3 -m analysis -a process -i gcp -m super -p ${GPREFIX}

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
	@python3 -m pytest -v test/ -k Lemon -s
