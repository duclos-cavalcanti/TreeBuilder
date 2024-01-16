#!/bin/bash 

git checkout uab
cd gcp-deploy

python3 run.py create-template -r 10 -p 3 -b 2 -c 1 -rm socket -dm standard -conf 0
