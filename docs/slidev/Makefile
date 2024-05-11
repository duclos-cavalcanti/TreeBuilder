ifeq (, $(shell which docker))
$(error docker not found)
endif

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

DOCKER := tangramor/slidev:latest
NAME := slidev-ma

.PHONY: run stop exit clean
all: run

run:
	docker run --name ${NAME} --rm -it \
    --user node \
    -v ${PWD}:/slidev \
    -p 3031:3030 \
    -e NPM_MIRROR="https://registry.npmmirror.com" \
    ${DOCKER}

exit:
	$(error Exiting Makefile)

stop: $(if $(shell docker ps --filter "name=${NAME}" --format "{{.ID}}") , ,exit)
	@docker stop $(shell docker ps --filter "name=${NAME}" --format "{{.ID}}")

clean:
	@echo clean
