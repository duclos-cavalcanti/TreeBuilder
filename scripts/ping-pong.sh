#!/bin/bash 

# 1. ssh into node 1 
# 2. ping <ip address of node 2> # 192.168.1.2
ping 192.168.1.2

# ---------------

# 1. ssh into node 2
# 2. Using `nc` to listen on a specific PORT and IP, run: nc -l -p <port> -s <ip>
nc -l -p 12345 -s 192.168.1.2

