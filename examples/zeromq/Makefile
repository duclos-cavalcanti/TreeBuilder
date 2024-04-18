CC = g++
CFLAGS := -Wall -Wextra -std=c++17 -Wno-missing-field-initializers -DZMQ_BUILD_DRAFT_API=1
CFLAGS += $(shell pkg-config --libs --cflags cppzmq) 
LDFLAGS = -L/usr/lib

SRCS := $(wildcard *.cpp)

.PHONY: all build

all: build

build: $(SRCS) Makefile
	$(CC) $(CFLAGS) $(SRCS) -o ./bin $(LDFLAGS)
	@echo "BUILT"

clean:
	rm -f ./bin
