#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test DMRS XML
Latest version can be found at https://github.com/letuananh/intsem.fx

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
__credits__ = [ "Le Tuan Anh" ]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import unittest

from visualkopasu.config import Biblioteca
from visualkopasu.kopasu.util import getSentenceFromXMLString
from visualkopasu.kopasu.util import getDMRSFromXMLString

########################################################################

class TestDMRSXML(unittest.TestCase):
    
    redwoods = Biblioteca('redwoods')
    corpus_name = 'redwoods'
    doc_name = 'cb'

    def test_text_dao(self):        
        print("test text DAO")
        # get all sentences
        cbdao = self.redwoods.textdao.getCorpusDAO(self.corpus_name).getDocumentDAO(self.doc_name)
        sentences = cbdao.getSentences()
        self.assertTrue(sentences)

        # test first sentence
        sentence = cbdao.getSentence(sentences[0])
        validate_sentence(self, sentence)
        # test first interpretation
        interpretation = cbdao.getDMRSRaw(sentences[0], '0', False)
        self.assertTrue(interpretation)
        interpretation = cbdao.getDMRSRaw(sentences[0], '0', True)
        self.assertTrue(interpretation)

    def test_sql_dao(self):
        print("test sql DAO")
        corpusdao = self.redwoods.sqldao
        # get document 
        cb = corpusdao.getDocumentByName(self.doc_name)[0]
        sentences = corpusdao.getSentences(cb.ID)
        self.assertTrue(sentences)

        sentence = corpusdao.getSentence(sentences[0].ID)
        validate_sentence(self, sentence)

    def test_xml_to_dmrs(self):
        cbdao = self.redwoods.textdao.getCorpusDAO(self.corpus_name).getDocumentDAO(self.doc_name)
        xmlstr = cbdao.getDMRSRaw(1010, 0, True)[0]
        print(xmlstr)
        dmrsobj = getDMRSFromXMLString(xmlstr)
        self.assertTrue(dmrsobj)
        print(dmrsobj)

def validate_sentence(self, sentence):
    self.assertIsNotNone(sentence)
    self.assertTrue(sentence.interpretations)
    self.assertTrue(sentence.interpretations[0])
    self.assertTrue(sentence.interpretations[0].dmrs[0])
    print(sentence)

########################################################################

def main():
    unittest.main()

if __name__ == "__main__":
    main()
