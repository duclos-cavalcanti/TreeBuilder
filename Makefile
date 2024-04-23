PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

.PHONY: exs tar docker vagrant clean
all:

exs:
	@tar --exclude=bin \
		 -zcvf ./examples.tar.gz ./examples

tar:
	@tar --exclude=jasper \
		 --exclude=project.tar.gz \
		 --exclude=.git \
		 --exclude=.gitkeep \
		 --exclude=.gitignore \
		 --exclude=.gitmodules \
		 --exclude=examples \
		 --exclude=lib \
		 --exclude=build \
		 --exclude=.cache \
		 --exclude=terra \
		 --exclude=infra \
		 --exclude=analysis \
		 --exclude-vcs-ignores \
		 -zcvf project.tar.gz .

docker-base:
	$(MAKE) -C ./infra/packer/ docker

docker: docker-base tar
	@cp -v project.tar.gz ./infra/terra/docker/extract
	$(MAKE) -C ./infra/terra/ docker

vagrant-base:
	$(MAKE) -C ./infra/packer/ vagrant

vagrant:
	$(MAKE) -C ./infra/terra/ docker

clean:
	$(MAKE) -C ./infra/terra/ clean

