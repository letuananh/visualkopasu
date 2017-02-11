#!/bin/bash

# python -m unittest discover
# python3 -m unittest test.test_dmrs_query
# python3 -m unittest test.test_dmrs_dao
# python3 -m unittest test.test_setup
# python3 -m unittest test.test_search
python3 -m unittest discover -s test

# to run a specific test case:
# python3 -m unittest test.test_dmrs_dao.TestDMRSDAO.test_xml_file_to_dmrs
