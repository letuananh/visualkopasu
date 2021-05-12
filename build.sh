#!/bin/bash

find . -name "*.pyc" -exec rm -rf {} \;
find . -name "*.py~" -exec rm -rf {} \;
find . -name "__pycache__" -exec rm -rf {} \;


tar -zcvf dist/visko_site.tar.gz visko_site manage.py
