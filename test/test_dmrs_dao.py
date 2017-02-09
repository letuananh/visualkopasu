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

import os
import unittest

from coolisf.util import Grammar

from visualkopasu.config import Biblioteca
from visualkopasu.config import ViskoConfig as vkconfig
from visualkopasu.console.setup import prepare_database
from visualkopasu.kopasu.util import getSentenceFromXMLString
from visualkopasu.kopasu.util import getDMRSFromXMLString
from visualkopasu.kopasu.util import getDMRSFromXML
from visualkopasu.kopasu.util import RawXML
from visualkopasu.kopasu.models import Corpus
from visualkopasu.kopasu.models import Document
from visualkopasu.kopasu.models import ParseRaw

########################################################################


TEST_FILE = 'data/speckled_10565.xml'


class TestRawXML(unittest.TestCase):

    def test_read_from_xml(self):
        raw = RawXML.from_file(TEST_FILE)
        self.assertEqual(raw.text, 'I took a step forward.')
        self.assertEqual(len(raw), 1)
        # should have both MRS and DMRS
        self.assertGreater(len(raw[0].mrs_str()), 0)
        # print(raw[0].mrs.text)
        self.assertGreater(len(raw[0].dmrs_str()), 0)
        # print(raw[0].dmrs_str())


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
        with open(TEST_FILE) as testfile:
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
            # there should be 2 raw (MRS in str mode and DMRS in xml mode)
            self.assertEqual(len(i.raws), 2)

    def test_xml_dao(self):
        print("Test ISF sense reading")
        ERG = Grammar()
        sent = ERG.txt2dmrs('The dog barks.')

        sent_node = sent.to_xml_node()
        sent_string = sent.to_xml_str()
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

    def ensure_corpus(self):
        ''' Ensure that testcorpus exists'''
        c = self.bib.sqldao.getCorpus(self.corpus_name)
        if not c:
            c = self.bib.sqldao.createCorpus(self.corpus_name)
        return self.bib.sqldao.getCorpus(self.corpus_name)[0]

    def ensure_doc(self):
        ''' Ensure that testcorpus exists'''
        corpus = self.ensure_corpus()
        docs = self.bib.sqldao.getDocumentByName(self.doc_name)
        if not docs:
            doc = Document(name=self.doc_name, corpusID=corpus.ID)
            self.bib.sqldao.saveDocument(doc)
        return self.bib.sqldao.getDocumentByName(self.doc_name)[0]

    def ensure_sent(self):
        doc = self.ensure_doc()
        with open(self.sentence_xml_file) as testfile:
            xmlstr = testfile.read()
            sentence = getSentenceFromXMLString(xmlstr)
            sentence.documentID = doc.ID
        sent = self.bib.sqldao.getSentence(sentenceID=1)
        if sent is None:
            self.bib.sqldao.saveSentence(sentence)
        return self.bib.sqldao.getSentence(sentenceID=1)

    def test_create_a_corpus(self):
        print("Test creating a new corpus")
        self.bib.sqldao.createCorpus(self.corpus_name)

        # test retriving created corpus
        corpus = self.bib.sqldao.getCorpus(self.corpus_name)[0]
        self.assertIsNotNone(corpus)
        self.assertIsNotNone(corpus.name)

    def test_create_document(self):
        print("Test creating document")
        corpus = self.ensure_corpus()
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

        doc = self.ensure_doc()
        sentence.documentID = doc.ID
        sentence = self.bib.sqldao.saveSentence(sentence)

        # verify that the sentence has been inserted
        actual_sentence = self.bib.sqldao.getSentence(sentenceID=sentence.ID)
        self.assertIsNotNone(actual_sentence.ID)
        self.assertEqual(actual_sentence.text, sentence.text)
        self.assertGreater(len(actual_sentence), 0)
        self.assertEqual(len(actual_sentence[0].raws), 2)
        self.assertEqual(actual_sentence[0].raws[0].rtype, ParseRaw.MRS)
        self.assertEqual(actual_sentence[0].raws[1].rtype, ParseRaw.XML)
        self.assertGreater(len(actual_sentence[0].raws[0].text), 0)
        self.assertGreater(len(actual_sentence[0].raws[1].text), 0)
        self.assertEqual(str(actual_sentence[0].raws[0]), '[mrs:[ LTOP: h0 INDEX: e2 [ e ...CONS: < e21 topic x16 > ]]')
        self.assertEqual(str(actual_sentence[0].raws[1]), '[xml:<dmrs cfrom="-1" cto="-1"...st>H</post></link></dmrs>]')

    def test_storing_parse_raw(self):
        # Test creating parse_raw object
        raw = ParseRaw('<xml></xml>', rtype=ParseRaw.XML)
        self.assertEqual(raw.rtype, ParseRaw.XML)
        jraw = ParseRaw()
        self.assertEqual(jraw.rtype, ParseRaw.JSON)

        # Test empty select
        sent = self.ensure_sent()
        self.assertIsNotNone(sent)
        self.assertGreater(len(sent), 0)
        raw.interpretationID = sent[0].ID
        self.bib.sqldao.saveParseRaw(raw)
        raws = self.bib.sqldao.get_raw(sent[0].ID)
        self.assertGreater(len(raws), 0)
        print(raws)
        pass

########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
