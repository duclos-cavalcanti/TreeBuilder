CC = g++
CFLAGS = -Wall -Wextra -std=c++17 -Wno-missing-field-initializers
LDFLAGS = -luring -lpthread -L/usr/lib -lbpf

HDRS = $(wildcard *.h)
SRCS = $(wildcard *.cpp)
OBJS = $(SRCS:.cpp=.o)
CONFIG := $(shell pkg-config --path libdpdk)

.PHONY: build run
all: build

recipient: $(CONFIG)
	$(CC) $(SRCS) $(CFLAGS) -o $@ $(LDFLAGS) `pkg-config --cflags --libs protobuf` `pkg-config --cflags --libs libdpdk`

build: recipient

run: recipient
	./recipient

clean:
	rm -f recipient $(OBJS)
