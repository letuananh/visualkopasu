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
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import sys
import os
import unittest

from coolisf.util import Grammar
from coolisf.gold_extract import sentence_to_xml
from coolisf.gold_extract import sentence_to_xmlstring

from visualkopasu.config import Biblioteca
from visualkopasu.config import ViskoConfig as vkconfig
from visualkopasu.console.setup import prepare_database
from visualkopasu.kopasu.util import getSentenceFromXMLString
from visualkopasu.kopasu.util import getDMRSFromXMLString
from visualkopasu.kopasu.util import getDMRSFromXML
from visualkopasu.kopasu.models import Corpus
from visualkopasu.kopasu.models import Document

########################################################################


class TestDMRSDAO(unittest.TestCase):
    testbib = Biblioteca('test')
    corpus_name = 'minicb'
    doc_name = 'cb100'

    def test_text_dao(self):
        print("test text DAO")
        # get all sentences
        cbdao = self.testbib.textdao.getCorpusDAO(self.corpus_name).getDocumentDAO(self.doc_name)
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
        corpusdao = self.testbib.sqldao
        # get document 
        cb = corpusdao.getDocumentByName(self.doc_name)[0]
        sentences = corpusdao.getSentences(cb.ID)
        self.assertTrue(sentences)

        sentence = corpusdao.getSentence(sentences[0].ID)
        validate_sentence(self, sentence)

    def test_xml_to_dmrs(self):
        cbdao = self.testbib.textdao.getCorpusDAO(self.corpus_name).getDocumentDAO(self.doc_name)
        xmlstr = cbdao.getDMRSRaw(1010, 0, True)[0]
        # print(xmlstr)
        dmrsobj = getDMRSFromXMLString(xmlstr)
        self.assertTrue(dmrsobj)

    def test_xml_file_to_dmrs(self):
        print("Test XML parser")
        with open('data/speckled_10565.xml') as testfile:
            xmlstr = testfile.read()
            # print(">>>", xmlstr)
            sentobj = getSentenceFromXMLString(xmlstr)
            self.assertTrue(sentobj)
            self.assertTrue(sentobj.interpretations)
            i = sentobj.interpretations[0]
            d = i.dmrs[0]
            self.assertTrue(d.nodes)
            self.assertTrue(d.links)
            self.assertTrue(d.nodes[2].sense)
            for n in d.nodes:
                if n.sense:
                    print(n.sense.synsetid)

    def test_xml_dao(self):
        print("Test ISF sense reading")
        ERG = Grammar()
        result = ERG.txt2dmrs('The dog barks.')
        sent_node = sentence_to_xml(result)
        self.assertTrue(sent_node)

        sent_string = sentence_to_xmlstring(result)
        with open('data/test_coolisf.xml', 'w') as outfile:
            outfile.write(sent_string)

        dmrses = sent_node.findall('./dmrses/dmrs')
        self.assertEqual(len(dmrses), 2)
        dmrs_obj = getDMRSFromXML(dmrses[0])
        self.assertTrue(dmrs_obj)
        for node in dmrs_obj.nodes:
            if node.sense:
                print(node.sense)
    # end test


def validate_sentence(self, sentence):
    self.assertIsNotNone(sentence)
    self.assertTrue(sentence.interpretations)
    self.assertTrue(sentence.interpretations[0])
    self.assertTrue(sentence.interpretations[0].dmrs[0])
    print(sentence)


class TestDMRSSQLite(unittest.TestCase):

    # We create a dummy corpora collection (visko unittest collection)
    bibname = 'vkutcol'
    corpus_name = 'testcorpus'
    doc_name = '1stdoc'
    sentence_xml_file = 'data/wndef_99.xml'
    bib = Biblioteca(bibname)

    @classmethod
    def setUpClass(cls):
        db_path = cls.bib.sqldao.db_path
        print("Setting up database file at %s" % (db_path,))
        # make sure we recreate the test DB every we run the test
        if os.path.isfile(db_path):
            os.unlink(db_path)
        prepare_database(vkconfig.BIBLIOTECHE_ROOT, cls.bibname)

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up")

    def test_create_a_corpus(self):
        print("Test creating a new corpus")
        self.bib.sqldao.createCorpus(self.corpus_name)

        # test retriving created corpus
        corpus = self.bib.sqldao.getCorpus(self.corpus_name)[0]
        self.assertIsNotNone(corpus)
        self.assertIsNotNone(corpus.name)

    def test_create_document(self):
        print("Test creating document")
        corpus = self.bib.sqldao.getCorpus(self.corpus_name)[0]
        doc = Document(name=self.doc_name, corpusID=corpus.ID)
        self.bib.sqldao.saveDocument(doc)

        # test retrieving doc
        doc = self.bib.sqldao.getDocumentByName(self.doc_name)[0]
        self.assertIsNotNone(doc)
        self.assertEqual(doc.name, self.doc_name)
        self.assertEqual(doc.corpusID, corpus.ID)

    def test_insert_sentence(self):
        with open(self.sentence_xml_file) as testfile:
            xmlstr = testfile.read()
        sentence = getSentenceFromXMLString(xmlstr)
        self.assertTrue(sentence.interpretations)
        print(sentence)

        # test save sentence
        doc = self.bib.sqldao.getDocumentByName(self.doc_name)[0]
        sentence.documentID = doc.ID
        sentence = self.bib.sqldao.saveSentence(sentence)

        # verify that the sentence has been inserted
        actual_sentence = self.bib.sqldao.getSentence(sentenceID=sentence.ID)
        self.assertIsNotNone(actual_sentence.ID)
        self.assertEqual(actual_sentence.text, sentence.text)
        self.assertTrue(actual_sentence.interpretations)


########################################################################

def main():
    unittest.main()

if __name__ == "__main__":
    main()
