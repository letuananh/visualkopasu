#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test Visko-ISF integration
Latest version can be found at https://github.com/letuananh/visualkopasu

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
# This file is part of VisualKopasu.
# VisualKopasu is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# VisualKopasu is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with VisualKopasu. If not, see http://www.gnu.org/licenses/.

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2016, visualkopasu"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import logging
import unittest

from coolisf import GrammarHub
from coolisf.model import MRS, DMRS
from visko.kopasu.xmldao import RawXML

########################################################################

logging.basicConfig(level=logging.WARNING)  # change to DEBUG for more info
TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.isdir(TEST_DIR):
    os.makedirs(TEST_DIR)
TEST_FILE = os.path.join(TEST_DIR, '10022.xml.gz')
TEST_FILE2 = os.path.join(TEST_DIR, '10044.xml.gz')

ghub = GrammarHub()
ERG = ghub.ERG


class TestRawXML(unittest.TestCase):

    ghub = GrammarHub()
    ERG = ghub.ERG

    def test_read_from_xml(self):
        raw = RawXML.from_file(TEST_FILE)
        self.assertEqual(raw.text, '"My name is Sherlock Holmes.')
        self.assertEqual(len(raw), 1)
        # should have both MRS and DMRS
        self.assertGreater(len(raw[0].mrs_str()), 0)
        logging.debug(raw[0].mrs.text)
        self.assertGreater(len(raw[0].dmrs_str()), 0)
        logging.debug(raw[0].dmrs_str())

    def test_read_10044(self):
        raw = RawXML.from_file(TEST_FILE2)
        # test RawXML.RawParse > DMRS and MRS
        m = MRS(raw[0].mrs.text)
        self.assertIsNotNone(m.obj())
        self.assertIsNotNone(m.to_dmrs())
        # save 10044 to XML file
        x = raw[0].dmrs_str()
        f = os.path.join(TEST_DIR, 'v10044.xml')
        with open(f, 'w') as outfile:
            outfile.write(x)
        # read it back
        print("Reading from {}".format(f))
        with open(f, 'r') as infile:
            x = infile.read()
            print(len(x))
            d = DMRS(x)
            self.assertIsNotNone(d.obj())
        # seems OK


########################################################################

if __name__ == "__main__":
    unittest.main()
