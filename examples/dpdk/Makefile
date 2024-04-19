ifeq (, $(shell which pkg-config))
$(error pkg-config not found)
endif

ifeq (, $(shell pkg-config --exists libdpdk && echo "DPDK FOUND"))
$(error pkg-config can't find dpdk)
endif

CC = gcc
CFLAGS := -Wall -Wextra -Wno-missing-field-initializers
CFLAGS += $(shell pkg-config --cflags libdpdk)
LFLAGS := -L/usr/lib
LFLAGS := $(shell pkg-config --libs libdpdk)

SRCS := $(wildcard *.c)
OBJS := $(SRCS:.c=.o)

NAME := bin

.PHONY: all build
all: build

$(OBJS): %.o : %.c
	$(CC) $(CFLAGS) -c $< -o $@

build: $(OBJS)
	$(CC) $(OBJS) ${CFLAGS} $(LFLAGS) -o ${NAME}

clean:
	rm -f *.o
	rm -f ${NAME}
