#!/bin/bash
if [ -z $1 ];then
  echo "usage: $0 <port>"
  exit
fi
echo "CONFUPDATE / HTTP/1.0"| nc localhost $1
