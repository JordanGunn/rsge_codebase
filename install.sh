#!/usr/bin/bash

# try pip in PATH
( \
  python3.11 -m pip install . || \
  \
  python3.10 -m pip install . || \
  \
  python3.9 -m pip install . || \
  \
  python3.8 -m pip install . || \
  \
  python3.7 -m pip install . || \
  \
  python3.6 -m pip install . || \
  \
  # linux system installation (pip3 in PATH)
  pip3 install . || \
  # pip in PATH
  pip install . || \
  \
  # try pip as python3 module (linux system installation)
  python3 -m pip3 install . || \
  python3 -m pip install . || \
  \
  # try pip as py module
  py -m pip3 install . || \
  py -m pip install . || \
  \
  # try pip as python module
  python -m pip3 install . || \
  python -m pip install . || \
  \
  # if all of those fail, exit with code 1
  exit 1
  \
) 2> /dev/null
