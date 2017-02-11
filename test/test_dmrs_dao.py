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

from chirptext.leutile import FileTool
from coolisf.util import Grammar

from visualkopasu.config import Biblioteca
from visualkopasu.console import prepare_database
from visualkopasu.kopasu.util import getSentenceFromXMLString
from visualkopasu.kopasu.util import getSentenceFromRawXML
from visualkopasu.kopasu.util import getSentenceFromFile
from visualkopasu.kopasu.util import getDMRSFromXML
from visualkopasu.kopasu.util import RawXML
from visualkopasu.kopasu.models import Document
from visualkopasu.kopasu.models import ParseRaw

########################################################################


TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_FILE = os.path.join(TEST_DIR, 'speckled_10565.xml')


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


class TestDAOBase(unittest.TestCase):

    # We create a dummy corpora collection (visko unittest collection)
    bibroot = os.path.join(TEST_DIR, 'bibcol')
    bibname = 'testbib'
    corpus_name = 'testcorpus'
    doc_name = '1stdoc'
    bib = Biblioteca(bibname, root=bibroot)

    @classmethod
    def setUpClass(cls):
        # prepare bibroot directory
        FileTool.create_dir(cls.bibroot)
        db_path = cls.bib.sqldao.db_path
        print("Setting up database file at %s" % (db_path,))
        # make sure we recreate the test DB every we run the test
        if os.path.isfile(db_path):
            os.unlink(db_path)
        prepare_database(cls.bibroot, cls.bibname, backup=False)

    @classmethod
    def tearDownClass(cls):
        print("Cleaning up")


class TestDMRSDAO(TestDAOBase):

    def test_creating_stuff(self):
        self.bib.textdao.createCorpus(self.corpus_name)
        cdao = self.bib.textdao.getCorpusDAO(self.corpus_name)
        self.assertTrue(os.path.isdir(cdao.path))
        # create doc
        cdao.create_doc(self.doc_name)
        ddao = cdao.getDocumentDAO(self.doc_name)
        self.assertTrue(os.path.isdir(ddao.path))
        # clear doc first
        sentids = ddao.getSentences()
        for sentid in sentids:
            ddao.delete_sent(sentid)
        # create sentences
        ddao.add_sentence(os.path.join(TEST_DIR, 'test1.xml.gz'))
        ddao.add_sentence(os.path.join(TEST_DIR, 'test2.xml.gz'))
        ddao.add_sentence(os.path.join(TEST_DIR, 'test1.xml.gz'), 1)
        ddao.add_sentence(os.path.join(TEST_DIR, 'test2.xml.gz'), 2)
        sentids = ddao.getSentences()
        self.assertEqual(len(sentids), 4)
        # now delete 2 of them
        ddao.delete_sent('test1')
        ddao.delete_sent('test2')
        # now we should have only 2 sentences
        sentids = ddao.getSentences()
        self.assertEqual(len(sentids), 2)

        # test first sentence
        sentence = ddao.getSentence(sentid[0])
        validate_sentence(self, sentence)

    def test_parse_xml_file(self):
        print("Test XML parser")
        sent = getSentenceFromFile(TEST_FILE)
        self.assertTrue(sent)
        self.assertTrue(sent.interpretations)
        i = sent.interpretations[0]
        d = i.dmrs[0]
        self.assertTrue(d.nodes)
        self.assertTrue(d.links)
        self.assertTrue(d.nodes[2].sense)
        # there should be 2 raw (MRS in str mode and DMRS in xml mode)
        self.assertEqual(len(i.raws), 2)
        for raw in i.raws:
            print(raw)

    def test_xml_dao(self):
        print("Test ISF sense reading")
        ERG = Grammar()
        sent = ERG.txt2dmrs('The dog barks.')
        # ISF sentence can be exported to visko directly
        sent_node = sent.to_visko_xml()
        self.assertIsNotNone(sent_node)
        # sentence string
        sent_string = sent.to_visko_xml_str()
        self.assertGreater(len(sent_string), 0)
        with open(os.path.join(TEST_DIR, 'test_coolisf.xml'), 'w') as outfile:
            outfile.write(sent_string)

    def test_dmrs_from_coolisf(self):
        # use CoolISF to generate Visko sentence XML
        ERG = Grammar()
        sent = ERG.txt2dmrs('I saw a girl with a telescope which is nice.', parse_count=10)
        raw = RawXML(xml=sent.to_visko_xml())
        self.assertEqual(len(raw), 10)
        #
        # test parse DMRS from DMRS XML node
        dmrs_obj = getDMRSFromXML(raw[0].dmrs)
        self.assertTrue(dmrs_obj)
        for node in dmrs_obj.nodes:
            if node.sense:
                print(node.sense)
        #
        # test parse the whole  sentence
        sent = getSentenceFromRawXML(raw)
        self.assertEqual(len(sent), 10)
        self.assertEqual(len(sent[0].raws), 2)
        self.assertEqual(sent[0].raws[0].rtype, ParseRaw.MRS)
        self.assertEqual(sent[0].raws[1].rtype, ParseRaw.XML)
    # end test


def validate_sentence(self, sentence):
    self.assertIsNotNone(sentence)
    self.assertTrue(sentence.interpretations)
    self.assertTrue(sentence.interpretations[0])
    self.assertTrue(sentence.interpretations[0].dmrs[0])
    print(sentence)


class TestDMRSSQLite(TestDAOBase):

    def ensure_corpus(self):
        ''' Ensure that testcorpus exists'''
        print("Test bib loc: {}".format(self.bib.sqldao.db_path))
        self.bib.create_corpus(self.corpus_name)
        c = self.bib.sqldao.getCorpus(self.corpus_name)
        return c[0]

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
        sent = getSentenceFromFile(TEST_FILE)
        sent.documentID = doc.ID
        sent = self.bib.sqldao.getSentence(sentenceID=1)
        if sent is None:
            self.bib.sqldao.saveSentence(sent)
        return self.bib.sqldao.getSentence(sentenceID=1)

    def test_create_a_corpus(self):
        print("Test creating a new corpus")
        self.bib.create_corpus(self.corpus_name)
        # test retriving created corpus
        print("Connecting to {}".format(self.bib.sqldao.db_path))
        corpora = self.bib.sqldao.getCorpus(self.corpus_name)
        self.assertIsNotNone(corpora)
        self.assertGreater(len(corpora), 0)
        self.assertEqual(corpora[0].name, self.corpus_name)
        # we should have an SQLite DB file ...
        self.assertTrue(os.path.isfile(self.bib.sqldao.db_path))
        # and a directory to store XML files
        # text collection must exist
        print("XMLCorpusCollection loc: {}".format(self.bib.textdao.path))
        self.assertTrue(os.path.isdir(self.bib.textdao.path))
        # corpus folder must exist as well
        cdao = self.bib.textdao.getCorpusDAO(self.corpus_name)
        self.assertTrue(os.path.isdir(cdao.path))

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
        sentence = getSentenceFromFile(TEST_FILE)
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
        self.assertEqual(str(actual_sentence[0].raws[0]), '[mrs:[ LTOP: h0 INDEX: e2 [ e ...10 qeq h12 > ICONS: < > ]]')
        self.assertEqual(str(actual_sentence[0].raws[1]), '[xml:<dmrs cfrom="-1" cto="-1"...   </link>\n    </dmrs>]')

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
