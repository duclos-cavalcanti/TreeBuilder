ifeq (, $(shell which docker))
$(error docker not found)
endif

PWD := $(shell pwd)
UID := $(shell id -u)
GID := $(shell id -g)

DOCKER := tangramor/slidev:playwright
NAME := slidev-ma

.PHONY: pres pdf build stop exit clean
all: pres

pres:
	docker run --name ${NAME} --rm -it \
    --user node \
    -v ${PWD}:/slidev \
    -p 3031:3030 \
    -e NPM_MIRROR="https://registry.npmmirror.com" \
    ${DOCKER}

pdf: 
	docker exec -i ${NAME} npx playwright install
	docker exec -i ${NAME} npx slidev export --timeout 2m --output slides.pdf

build: 
	docker exec -i ${NAME} npx slidev build

exit:
	$(error Exiting Makefile)

stop: $(if $(shell docker ps --filter "name=${NAME}" --format "{{.ID}}") , ,exit)
	@docker stop $(shell docker ps --filter "name=${NAME}" --format "{{.ID}}")

clean:
	@echo clean
