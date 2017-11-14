#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test script for utils
Latest version can be found at https://github.com/letuananh/VisualKopasu

References:
    Python unittest documentation:
        https://docs.python.org/3/library/unittest.html
    Python documentation:
        https://docs.python.org/
    PEP 0008 - Style Guide for Python Code
        https://www.python.org/dev/peps/pep-0008/
    PEP 0257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2017, VisualKopasu"
__license__ = "MIT"
__maintainer__ = "Le Tuan Anh"
__version__ = "0.1"
__status__ = "Prototype"
__credits__ = []

########################################################################

import os
import unittest
from visko.util import Paginator, PaginationException

# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DATA = os.path.join(TEST_DIR, 'data')


# -------------------------------------------------------------------------------
# Test cases
# -------------------------------------------------------------------------------

class TestUtils(unittest.TestCase):

    def test_pagination(self):
        # test invalid
        self.assertRaises(PaginationException, lambda: Paginator(pagesize=-10, windowpane=2))
        self.assertRaises(PaginationException, lambda: Paginator(pagesize=10, windowpane=-2))
        self.assertRaises(PaginationException, lambda: Paginator(pagesize=10, windowpane=0))
        self.assertRaises(PaginationException, lambda: Paginator(pagesize=0, windowpane=2))
        # Test paginator
        pager = Paginator(pagesize=10, windowpane=2)
        self.assertEqual(pager.total(0), 0)
        self.assertEqual(pager.total(100), 10)
        self.assertEqual(pager.total(101), 11)
        # test invalid parameters
        self.assertRaises(PaginationException, lambda: pager.total(-1))
        self.assertRaises(PaginationException, lambda: pager.total(None))
        self.assertRaises(PaginationException, lambda: pager.paginate(None, 10))
        self.assertRaises(PaginationException, lambda: pager.paginate(5, None))
        # test pagination
        # [0] 1 2 3 4
        pg = pager.paginate(0, 10)
        self.assertTrue(pg.is_first)
        self.assertFalse(pg.is_last)
        self.assertEqual(list(pg.left_pages), [])
        self.assertEqual(list(pg.right_pages), [1, 2, 3, 4])
        # 0 [1] 2 3 4
        pg = pager.paginate(1, 10)
        self.assertFalse(pg.is_first)
        self.assertFalse(pg.is_last)
        self.assertEqual(list(pg.left_pages), [0])
        self.assertEqual(list(pg.right_pages), [2, 3, 4])
        # 3 4 [5] 6 7
        pg = pager.paginate(5, 10)
        self.assertFalse(pg.is_first)
        self.assertFalse(pg.is_last)
        self.assertEqual(list(pg.left_pages), [3, 4])
        self.assertEqual(list(pg.right_pages), [6, 7])
        #  5 6 7 [8] 9
        pg = pager.paginate(8, 10)
        self.assertFalse(pg.is_first)
        self.assertFalse(pg.is_last)
        self.assertEqual(list(pg.left_pages), [5, 6, 7])
        self.assertEqual(list(pg.right_pages), [9])
        #  5 6 7 8 [9]
        pg = pager.paginate(9, 10)
        self.assertFalse(pg.is_first)
        self.assertTrue(pg.is_last)
        self.assertEqual(list(pg.left_pages), [5, 6, 7, 8])
        self.assertEqual(list(pg.right_pages), [])
        #  5 6 7 8 [9]
        pg = Paginator(windowpane=3).paginate(7, 10)
        self.assertFalse(pg.is_first)
        self.assertFalse(pg.is_last)
        self.assertEqual(list(pg.left_pages), [3, 4, 5, 6])
        self.assertEqual(list(pg.right_pages), [8, 9])


# -------------------------------------------------------------------------------
# Main method
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
