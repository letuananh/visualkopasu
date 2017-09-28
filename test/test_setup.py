#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test setup script
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

# Copyright (c) 2016, Le Tuan Anh <tuananh.ke@gmail.com>
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

import unittest

from visko.kopasu import Biblioteca

########################################################################


class TestConsoleSetup(unittest.TestCase):

    def test_setup(self):
        collection_name = 'gold'
        corpus_name = 'erg'
        doc_name = 'cb'
        bib = Biblioteca(collection_name)
        cbdao = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc_name)
        # make sure that archive exists
        self.assertTrue(cbdao.is_archived())
        doc = cbdao.read_archive()
        self.assertIsNotNone(doc)
        self.assertEqual(len(doc), 769)
        # test iter_archive
        self.assertEqual(len(list(cbdao.iter_archive())), len(doc))


########################################################################

if __name__ == "__main__":
    unittest.main()
