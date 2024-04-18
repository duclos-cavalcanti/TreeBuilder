CC = g++
CFLAGS := -Wall -Wextra -std=c++17 -Wno-missing-field-initializers
LDFLAGS = -L/usr/lib

SRCS := $(wildcard *.cpp)

.PHONY: all build

all: build

build: $(SRCS) Makefile
	$(CC) $(CFLAGS) $(SRCS) -o ./bin $(LDFLAGS)
	@echo "BUILT"

clean:
	rm -f ./bin
