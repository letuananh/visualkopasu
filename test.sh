#!/bin/bash

# python -m unittest discover
python3 -m unittest test.test_dmrs_query
python3 -m unittest test.test_dmrs_dao
python3 -m unittest test.test_setup
python3 -m unittest test.test_search
