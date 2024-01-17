#!/bin/bash 

sudo su 
cd /home/uab2005/dom-tenant-service/src
./build/multicast_client -a mac -t 10 -i 0 -s test
./build/multicast_client -a messages -t 10 -i 0 -s test
