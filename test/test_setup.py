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

# import sys
import os
import unittest

from visualkopasu.config import Biblioteca

from visualkopasu.console.setup import prepare_database
from visualkopasu.console.setup import parse_document
from visualkopasu.console.setup import get_raw_doc_folder
from visualkopasu.console.setup import convert_document
from .test_dmrs_dao import validate_sentence

########################################################################


class TestConsoleSetup(unittest.TestCase):

    def test_setup(self):
        collection_name = 'test'
        testbib = Biblioteca(collection_name)
        corpus_name = 'minicb'
        doc_name = 'cb100'

        # Test convert FCB format into VK standard XML format
        print("Make sure that test collection is there")
        raw_folder = get_raw_doc_folder(collection_name, corpus_name, doc_name)
        self.assertTrue(os.path.isdir(raw_folder))

        # Make sure that the test SQLite collection does not exist before this test
        if os.path.isfile(testbib.sqldao.db_path):
            os.unlink(testbib.sqldao.db_path)
        # prepare_database(testbib.root, collection_name)

        # clean file before convert
        print("Make sure that we deleted sentence 1010 before test parsing")
        cb100dao = testbib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc_name)
        sent1010_path = cb100dao.getPath(1010)
        print("sent1010_path = %s" % (sent1010_path,))
        if sent1010_path and os.path.isfile(sent1010_path):
            os.unlink(sent1010_path)

        parse_document(raw_folder, testbib.textdao.path, corpus_name, doc_name)

        print("Test generated XML file")
        # sent1010 = cb100dao.getSentence(1010)
        # validate_sentence(self, sent1010)
        convert_document(collection_name, corpus_name, doc_name)

        print("DB: %s" % (testbib.sqldao.db_path,))
        sentsql = testbib.sqldao.getSentence(1)
        print("sentsql = %s" % (sentsql,))
        validate_sentence(self, sentsql)


########################################################################

def main():
    unittest.main()


if __name__ == "__main__":
    main()
