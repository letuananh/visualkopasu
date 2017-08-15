#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test DMRS DAO
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

import os
import logging
import unittest

from chirptext.leutile import FileHelper
from chirptext.deko import txt2mecab
from chirptext.texttaglib import TaggedSentence
from coolisf.util import GrammarHub
from coolisf import Lexsem, tag_gold

from visko.kopasu.xmldao import getSentenceFromRawXML
from visko.kopasu.xmldao import getSentenceFromFile, getSentenceFromXML
from visko.kopasu.xmldao import getDMRSFromXML
from visko.kopasu.xmldao import RawXML
from visko.kopasu.dao import SQLiteCorpusDAO
from visko.kopasu.bibman import Biblioteche, Biblioteca
from visko.kopasu.models import Document
from visko.kopasu.models import ParseRaw


#-----------------------------------------------------------------------
# CONFIGURATION
#-----------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)  # change to DEBUG for more info
TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_FILE = os.path.join(TEST_DIR, '1300.xml.gz')
TEST_FILE2 = os.path.join(TEST_DIR, '10022.xml.gz')


#-----------------------------------------------------------------------
# TESTS
#-----------------------------------------------------------------------

class TestDAOBase(unittest.TestCase):

    # We create a dummy corpora collection (visko unittest collection)
    bibroot = os.path.join(TEST_DIR, 'bibcol')
    bibname = 'testbib'
    corpus_name = 'testcorpus'
    doc_name = '1stdoc'
    bib = Biblioteca(bibname, root=bibroot)
    ghub = GrammarHub()
    ERG = ghub.ERG
    db = SQLiteCorpusDAO(":memory:", "memdb")

    @classmethod
    def setUpClass(cls):
        logging.info("Preparing test class")
        # prepare bibroot directory
        FileHelper.create_dir(cls.bibroot)
        db_path = cls.bib.sqldao.db_path
        logging.debug("Setting up database file at %s" % (db_path,))

    @classmethod
    def tearDownClass(cls):
        logging.debug("Cleaning up")

    def ensure_corpus(self):
        ''' Ensure that testcorpus exists'''
        logging.debug("Test bib loc: {}".format(self.bib.sqldao.db_path))
        # ensure corpus
        corpuses = self.bib.sqldao.getCorpus(self.corpus_name)
        if not corpuses:
            self.bib.create_corpus(self.corpus_name)
            corpus = self.bib.sqldao.getCorpus(self.corpus_name)[0]
        else:
            corpus = corpuses[0]
        return corpus

    def ensure_doc(self):
        ''' Ensure that testcorpus exists'''
        corpus = self.ensure_corpus()
        docs = self.bib.sqldao.getDocumentByName(self.doc_name)
        if not docs:
            doc = Document(name=self.doc_name, corpusID=corpus.ID)
            self.bib.sqldao.saveDocument(doc)
        else:
            doc = docs[0]
        return doc

    def ensure_sent(self):
        doc = self.ensure_doc()
        sent = getSentenceFromFile(TEST_FILE)
        sent.documentID = doc.ID
        sent_obj = self.bib.sqldao.getSentence(sentenceID=1)
        if sent_obj is None:
            return self.bib.sqldao.saveSentence(sent)
        else:
            return sent_obj


class TestDMRSDAO(TestDAOBase):

    def test_parse_xml_file(self):
        logging.info("Test XML parser")
        sent = getSentenceFromFile(TEST_FILE)
        self.assertTrue(sent)
        self.assertTrue(sent.readings)
        i = sent.readings[0]
        d = i.dmrs[0]
        self.assertTrue(d.nodes)
        self.assertTrue(d.links)

    def test_xml_dao(self):
        logging.info("Test ISF sense reading")
        sent = self.ERG.parse('The dog barks.')
        # ISF sentence can be exported to visko directly
        sent_node = sent.to_visko_xml()
        self.assertIsNotNone(sent_node)
        # sentence string
        sent_string = sent.to_visko_xml_str()
        self.assertGreater(len(sent_string), 0)
        with open(os.path.join(TEST_DIR, 'test_coolisf.xml'), 'w') as outfile:
            outfile.write(sent_string)

    def test_dmrs_to_str(self):
        # an extended DMRS string representation (with sense tag)
        txt = 'It rains.'
        s = self.ERG.parse(txt)
        s.tag(method='mfs')  # fast tagging
        # bring it to visko
        vs = getSentenceFromXML(s.to_visko_xml())
        logger.debug(vs[0].dmrs[0])

    def test_dmrs_from_coolisf(self):
        # use CoolISF to generate Visko sentence XML
        sent = self.ERG.parse('I saw a girl with a telescope which is nice.', parse_count=10)
        raw = RawXML(xml=sent.to_visko_xml())
        self.assertEqual(len(raw), 10)
        #
        # test parse DMRS from DMRS XML node
        dmrs_obj = getDMRSFromXML(raw[0].dmrs)
        self.assertTrue(dmrs_obj)
        for node in dmrs_obj.nodes:
            if node.sense:
                logging.debug(node.sense)
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
    self.assertTrue(sentence.readings)
    self.assertTrue(sentence.readings[0])
    self.assertTrue(sentence.readings[0].dmrs[0])
    logging.debug(sentence)


class TestDMRSSQLite(TestDAOBase):

    def test_list_collections(self):
        self.ensure_corpus()
        bibs = Biblioteche.list_all(self.bibroot)
        self.assertGreaterEqual(len(bibs), 1)
        self.assertIn(self.bibname, bibs)

    def test_create_a_corpus(self):
        logging.info("Test creating a new corpus")
        self.ensure_corpus()
        corpora = self.bib.sqldao.getCorpus(self.corpus_name)
        self.assertIsNotNone(corpora)
        self.assertGreater(len(corpora), 0)
        self.assertEqual(corpora[0].name, self.corpus_name)
        # we should have an SQLite DB file ...
        self.assertTrue(os.path.isfile(self.bib.sqldao.db_path))
        # and a directory to store XML files
        # text collection must exist
        self.assertTrue(os.path.isdir(self.bib.textdao.path))
        # corpus folder must exist as well
        cdao = self.bib.textdao.getCorpusDAO(self.corpus_name)
        self.assertTrue(os.path.isdir(cdao.path))

    def test_create_document(self):
        logging.info("Test creating document")
        corpus = self.ensure_corpus()
        doc = self.ensure_doc()
        # test retrieving doc
        doc = self.bib.sqldao.getDocumentByName(self.doc_name)[0]
        self.assertIsNotNone(doc)
        self.assertEqual(doc.name, self.doc_name)
        self.assertEqual(doc.corpusID, corpus.ID)

    def test_insert_sentence(self):
        sentence = getSentenceFromFile(TEST_FILE2)
        self.assertTrue(sentence.readings)

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
        self.assertTrue(repr(actual_sentence[0].raws[0]).startswith('[mrs:[ TOP: '))
        self.assertTrue(repr(actual_sentence[0].raws[1]).startswith('[xml:<dmrs cfrom'))

    def test_get_sentences_with_dummy(self):
        doc = self.ensure_doc()
        self.ensure_sent()
        sents = self.bib.sqldao.getSentences(doc.ID, True)
        self.assertGreater(len(sents), 0)
        self.assertEqual(len(sents[0]), 1)
        self.assertIsNone(sents[0][0])

    def test_storing_parse_raw(self):
        # Test creating parse_raw object
        raw = ParseRaw('<xml></xml>', rtype=ParseRaw.XML)
        self.assertEqual(raw.rtype, ParseRaw.XML)
        jraw = ParseRaw()
        self.assertEqual(jraw.rtype, ParseRaw.XML)

        # Test empty select
        sent = self.ensure_sent()
        self.assertIsNotNone(sent)
        self.assertGreater(len(sent), 0)
        raw.readingID = sent[0].ID
        self.bib.sqldao.saveParseRaw(raw)
        raws = self.bib.sqldao.get_raw(sent[0].ID)
        self.assertGreater(len(raws), 0)
        logging.debug(raws)
        pass

    def test_doc(self):
        self.ensure_sent()
        dao = self.bib.sqldao
        doc = dao.getDocumentByName(self.doc_name)[0]
        # clear info
        # Test store grammar, tagger, parse_count and lang
        doc.grammar = None
        doc.tagger = None
        doc.parse_count = None
        doc.lang = None
        dao.saveDocument(doc)
        doc = dao.getDocumentByName(self.doc_name)[0]
        print(doc)
        self.assertIsNone(doc.grammar)
        self.assertIsNone(doc.tagger)
        self.assertIsNone(doc.parse_count)
        self.assertIsNone(doc.lang)
        # Test store grammar, tagger, parse_count and lang
        doc.grammar = "ERG"
        doc.tagger = "lelesk"
        doc.parse_count = 5
        doc.lang = "en"
        dao.saveDocument(doc)
        doc = dao.getDocumentByName(self.doc_name)[0]
        self.assertEqual(doc.grammar, "ERG")
        self.assertEqual(doc.tagger, "lelesk")
        self.assertEqual(doc.parse_count, 5)
        self.assertEqual(doc.lang, "en")

    def test_clear_doc_info(self):
        self.ensure_sent()
        dao = self.bib.sqldao
        doc = dao.getDocumentByName(self.doc_name)[0]
        # clear info
        # Test store grammar, tagger, parse_count and lang
        doc.grammar = None
        doc.tagger = None
        doc.parse_count = None
        doc.lang = None
        dao.saveDocument(doc)
        doc = dao.getDocumentByName(self.doc_name)[0]
        print(doc)
        self.assertIsNone(doc.grammar)
        self.assertIsNone(doc.tagger)
        self.assertIsNone(doc.parse_count)
        self.assertIsNone(doc.lang)


class TestHumanAnnotation(TestDAOBase):

    def clear_sents(self):
        doc = self.ensure_doc()
        sents = self.bib.sqldao.getSentences(doc.ID)
        for s in sents:
            self.bib.sqldao.delete_sent(s.ID)

    def test_adding_human_annotations(self):
        self.clear_sents()
        txt = "ロボットの子は猫が好きです。"
        sent = self.ghub.JACYMC.parse("ロボットの子は猫が好きです。", 1)
        self.assertGreaterEqual(len(sent), 1)
        # Create gold profile now ...
        tagged_sent = TaggedSentence(sent.text)
        words = txt2mecab(txt).words
        tagged_sent.import_tokens(words)
        # Add concepts
        tagged_sent.tag('ロボット', '02761392-n', 0)  # ロボット: 02761392-n
        tagged_sent.tag('猫', '02121620-n', 4)  # 猫: 02121620-n
        tagged_sent.tag('好き', '01292683-a', 6)  # 好き: 01292683-a
        # make robotto-no-ko a MWE
        tagged_sent.tag('ロボットの子', '10285313-n', 0, 1, 2)  # 子: 10285313-n (男の子)
        # Now perform sense-tagging
        tag_gold(sent[0].dmrs(), tagged_sent, sent.text, mode=Lexsem.STRICT)
        print(sent[0].dmrs().tags)
        # to visko
        vsent = getSentenceFromXML(sent.tag_xml().to_visko_xml())
        vsent.import_tags(tagged_sent)
        print(vsent.words)
        for c in vsent.concepts:
            print(c, c.words)
        # save to DB
        dao = self.bib.sqldao
        doc = self.ensure_doc()
        vsent.documentID = doc.ID
        dao.saveSentence(vsent)
        dao.save_annotations(vsent)

    def test_retrieving_annotations(self):
        txt = "ロボットの子は猫が好きです。"
        json_sent = {'tokens': [{'label': 'ロボット', 'cto': 4, 'cfrom': 0}, {'label': 'の', 'cto': 6, 'cfrom': 5}, {'label': '子', 'cto': 8, 'cfrom': 7}, {'label': 'は', 'cto': 10, 'cfrom': 9}, {'label': '猫', 'cto': 12, 'cfrom': 11}, {'label': 'が', 'cto': 14, 'cfrom': 13}, {'label': '好き', 'cto': 17, 'cfrom': 15}, {'label': 'です', 'cto': 20, 'cfrom': 18}, {'label': '。', 'cto': 22, 'cfrom': 21}], 'concepts': [{'clemma': 'ロボット', 'words': [0], 'tag': '02761392-n'}, {'clemma': '猫', 'words': [4], 'tag': '02121620-n'}, {'clemma': '好き', 'words': [6], 'tag': '01292683-a'}, {'clemma': 'ロボットの子', 'words': [0, 1, 2], 'tag': '10285313-n', 'flag': 'E'}], 'text': 'ロボット の 子 は 猫 が 好き です 。 \n'}
        # ISF sentence
        isent = self.ghub.JACYMC.parse(txt, 1)
        isent.shallow = TaggedSentence.from_json(json_sent)
        # save to Visko
        vxml = isent.tag_xml().to_visko_xml()
        vsent = getSentenceFromXML(vxml)
        dao = self.bib.sqldao
        doc = self.ensure_doc()
        vsent.documentID = doc.ID
        dao.saveSentence(vsent)  # this should save the annotations as well
        # retrieve them
        vsent2 = dao.get_annotations(vsent.ID)
        v2_json = vsent2.shallow.to_json()
        logger.debug("Words: {}".format(vsent2.words))
        logger.debug("Concepts: {}".format([(x, x.words) for x in vsent2.concepts]))
        logger.debug("v2_json: {}".format(v2_json))
        # compare to json_sent
        self.assertEqual(v2_json["text"], json_sent["text"])
        self.assertEqual(v2_json["tokens"], json_sent["tokens"])
        self.assertEqual(v2_json["concepts"], json_sent["concepts"])
        self.assertEqual(v2_json, json_sent)


########################################################################

if __name__ == "__main__":
    unittest.main()
