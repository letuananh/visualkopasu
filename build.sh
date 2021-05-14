#!/bin/bash

find . -name "*.pyc" -exec rm -rf {} \;
find . -name "*.py~" -exec rm -rf {} \;
find . -name "__pycache__" -exec rm -rf {} \;


tar -zcvf dist/visko.tar.gz visko_site manage.py requirements.txt LICENSE.txt README.md
