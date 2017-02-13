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
from lxml import etree
import unittest

from coolisf.util import Grammar
from visualkopasu.kopasu.util import getSentenceFromXML
from visualkopasu.kopasu.util import getSentenceFromFile
from visualkopasu.kopasu.util import parse_dmrs_str
from visualkopasu.kopasu.util import dmrs_str_to_xml

########################################################################

logging.basicConfig(level=logging.WARNING)  # change to DEBUG for more info
TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_FILE = os.path.join(TEST_DIR, '10565.xml.gz')


class TestMain(unittest.TestCase):

    def test_txt2isf(self):
        txt = 'Three musketeers and a giant walk into a bar.'
        # create a Grammar to parse text
        g = Grammar()
        isent = g.parse(txt, parse_count=10)
        self.assertEqual(len(isent), 10)
        # convert ISF sentence into an XML node
        xsent = isent.to_visko_xml()
        self.assertTrue(isinstance(xsent, etree._Element))
        # xsent to visko
        vsent = getSentenceFromXML(xsent)
        self.assertEqual(vsent.text, txt)
        self.assertEqual(len(vsent), 10)
        self.assertEqual(len(vsent.interpretations[0].raws), 2)

    def test_visko2isf(self):
        g = Grammar()
        isent = g.parse('I saw a girl with a telescope.', parse_count=10)
        vsent = getSentenceFromXML(isent.to_visko_xml())
        # convert back to isf
        isent2 = vsent.to_isf()
        self.assertIsNotNone(isent2)
        self.assertEqual(len(isent), len(isent2))

    def test_xml_to_txt(self):
        sent = getSentenceFromFile(TEST_FILE)
        logging.info("DMRS string: {}".format(sent[0].dmrs[0]))
        # tokens = simplemrs.tokenize(str(sent[0].dmrs[0]))
        # print(tokens)
        d = sent[0].dmrs[0]
        dmrs_dict = parse_dmrs_str(str(d))
        logging.info("DMRS dict: {}".format(dmrs_dict))
        # -1 because of root node (nodeid = 0)
        self.assertEqual(len(d.nodes) - 1, len(dmrs_dict['nodes']))
        self.assertEqual(len(d.links), len(dmrs_dict['links']))
        #
        dmrs_xml = dmrs_str_to_xml(str(d), sent.text)
        logging.info("DMRS XML: {}".format(dmrs_xml))


########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
