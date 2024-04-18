CC = gcc
CFLAGS := -Wall -Wextra -Wno-missing-field-initializers
LFLAGS := -L/usr/lib

SRCS := $(wildcard *.c)

.PHONY: all build

all: build

build: $(SRCS) Makefile
	$(CC) $(CFLAGS) $(SRCS) -o ./bin $(LDFLAGS)
	@echo "BUILT"

clean:
	rm -f ./bin
