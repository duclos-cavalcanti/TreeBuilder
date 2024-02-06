#!/bin/bash 

# dev related packages
{
    # installing neovim
    wget https://github.com/neovim/neovim/releases/download/nightly/nvim-linux64.tar.gz
    tar xzvf nvim-linux64.tar.gz
    cp ./nvim-linux64/bin/nvim /usr/local/bin
    cp -r ./nvim-linux64/share/* /usr/local/share
    cp -r ./nvim-linux64/lib/* /usr/local/lib
    
    # installing C/C++ LSP, man pages and more
    apt-get install clangd man-db ripgrep -yq
    unminimize
} &>> LOG.TXT

cd /root/work/module
bash
