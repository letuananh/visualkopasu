#!/bin/bash

find . -name "*.pyc" -exec rm -rf {} \;
find . -name "*.py~" -exec rm -rf {} \;
find . -name "__pycache__" -exec rm -rf {} \;

VISKO_VERSION=`python3 -m visko version -s`
tar -zcvf dist/visko-${VISKO_VERSION}.tar.gz visko_site manage.py requirements.txt LICENSE.txt README.md
