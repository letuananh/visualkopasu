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

from lxml import etree
import unittest

from coolisf.util import Grammar
from visualkopasu.kopasu.util import getSentenceFromXML

########################################################################


class TestMain(unittest.TestCase):

    def test_txt2isf(self):
        txt = 'Three musketeers and a giant walk into a bar.'
        # create a Grammar to parse text
        g = Grammar()
        isent = g.txt2dmrs(txt, parse_count=10)
        self.assertEqual(len(isent), 10)
        # convert ISF sentence into an XML node
        xsent = isent.to_visko_xml()
        self.assertTrue(isinstance(xsent, etree._Element))
        # xsent to visko
        vsent = getSentenceFromXML(xsent)
        self.assertEqual(vsent.text, txt)
        self.assertEqual(len(vsent), 10)
        self.assertEqual(len(vsent.interpretations[0].raws), 2)

########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
