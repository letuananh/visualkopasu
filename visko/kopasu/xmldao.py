'''
XML-based data access layer for VisualKopasu project.
@author: Le Tuan Anh
'''

# Copyright 2012, Le Tuan Anh (tuananh.ke@gmail.com)
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

import os.path
import shutil
import gzip
import codecs
import logging
import json
import lxml
from lxml import etree

from chirptext.texttaglib import TaggedSentence
from chirptext.leutile import FileHelper
from coolisf.util import is_valid_name
from coolisf.model import Sentence, Reading

from visko.util import getSubFolders, getFiles


logger = logging.getLogger(__name__)


class XMLBiblioteche:
    def __init__(self, root):
        """
        root: path to biblioteche folder
        """
        self.root = root

    def getCorpusCollection(self, collection_name):
        bibpath = os.path.join(self.root, collection_name)
        return XMLCorpusCollection(bibpath, collection_name)


class XMLCorpusCollection:
    def __init__(self, path, name):
        """
        root: path to collection folder
        """
        self.path = path
        self.name = name

    def getCorpusDAO(self, corpus_name):
        corpus_path = os.path.join(self.path, corpus_name)
        return XMLCorpusDAO(corpus_path, corpus_name)

    def create_corpus(self, corpus_name):
        if not is_valid_name(corpus_name):
            raise Exception("Invalid corpus name (provided: {}".format(corpus_name))
        FileHelper.create_dir(os.path.join(self.path, corpus_name))

    def getCorpora(self):
        ''' Get all available corpora
        '''
        return getSubFolders(self.path)


class XMLCorpusDAO:

    def __init__(self, path, name, collection=None):
        self.path = path
        self.name = name
        self.collection = collection

    def getDocumentDAO(self, doc_name):
        doc_path = os.path.join(self.path, doc_name)
        return XMLDocumentDAO(doc_path, doc_name)

    def create_doc(self, doc_name):
        if not is_valid_name(doc_name):
            raise Exception("Invalid doc name (provided: {}".format(doc_name))
        FileHelper.create_dir(os.path.join(self.path, doc_name))


class XMLDocumentDAO:

    def __init__(self, path, name, corpus=None):
        self.path = path
        self.name = name
        self.corpus = corpus

    def get_sents(self):
        all_files = [f.split('.')[0] for f in getFiles(self.path)]
        all_files.sort()
        return all_files

    def copy_sentence(self, sent_path, sentid=None):
        if sentid is not None and (not is_valid_name(sentid)):
            raise Exception("Invalid sentence ID (provided: {}".format(sentid))
        fname = '{}.xml.gz'.format(sentid) if sentid else os.path.basename(sent_path)
        target = os.path.join(self.path, fname)
        shutil.copy2(sent_path, target)

    def save_sentence(self, xmlcontent, sentid, pretty_print=True):
        if not is_valid_name(sentid):
            raise Exception("Invalid sentence ID (provided: {})".format(sentid))
        sent_path = os.path.join(self.path, str(sentid) + '.xml.gz')
        print("Saving to {}".format(sent_path))
        with gzip.open(sent_path, 'wb') as output_file:
            if isinstance(xmlcontent, lxml.etree._Element):
                xmlcontent = lxml.etree.tostring(xmlcontent, pretty_print=pretty_print, encoding='utf-8')
            else:
                xmlcontent = xmlcontent.encode('utf-8')
            output_file.write(xmlcontent)

    def delete_sent(self, sentid):
        file_path = self.getPath(sentid)
        if not file_path:
            raise Exception("Sentence {s} does not exist (path={p})".format(s=sentid, p=file_path))
        else:
            os.unlink(file_path)

    def getPath(self, sentid):
        if not sentid:
            raise Exception("sentence ID cannot be None")
        else:
            file_name = os.path.join(self.path, str(sentid) + '.xml.gz')
            file_name2 = os.path.join(self.path,
                                      "%s-%s.xml.gz" % (self.name, str(sentid)))
            logger.debug(("Filename1: %s" % file_name))
            logger.debug(("Filename2: %s" % file_name2))

            if os.path.isfile(file_name):
                return file_name
            elif os.path.isfile(file_name2):
                return file_name2
        return None

    def getSentenceRaw(self, sentid):
        # Parse the file
        full_path = self.getPath(sentid)
        logger.debug(full_path)
        with gzip.open(full_path, 'r') as gzfile:
            return gzfile.read()

    def get_sent(self, sentid):
        # Read raw text from file
        full_path = self.getPath(sentid)
        # Parse the file
        return getSentenceFromFile(full_path)


class RawXML(object):
    ''' Visko sentence in RAW XML format (preprocessor)
    '''

    def __init__(self, raw=None, xml=None):
        self.raw = raw  # XML string
        self.text = ''
        self.xml = xml
        self.parses = []
        if self.raw is not None or self.xml is not None:
            self.parse()

    def parse(self):
        if self.raw is not None:
            logger.debug("RawXML: creating XML object from XML string")
            self.xml = etree.XML(self.raw)
        else:
            self.raw = etree.tostring(self.xml, encoding='utf-8', pretty_print=True).decode('utf-8')
        self.text = self.xml.find('text').text
        for p in self.xml.findall('reading'):
            mrs = p.findall('mrs')
            dmrs = p.findall('dmrs')
            parse = RawParse(p)
            if not mrs:
                logger.warning("MRS node does not exist")
            elif len(mrs) == 1:
                parse.mrs = mrs[0]
            else:
                logger.warning("Multiple MRS nodes")
            if dmrs is not None and len(dmrs) == 1:
                parse.dmrs = dmrs[0]
            else:
                logger.warning("Multiple DMRS nodes")
            self.parses.append(parse)

    def __iter__(self):
        return iter(self.parses)

    def __len__(self):
        return len(self.parses)

    def __getitem__(self, key):
        return self.parses[key]

    def __str__(self):
        return "{} ({} parse(s))".format(self.text, len(self))

    def to_isf(self):
        sent = Sentence(self.text)
        for p in self.parses:
            sent.add(mrs_str=p.mrs.text)
        return sent

    @staticmethod
    def from_file(filename):
        ''' Read RawXML from .xml file or .gz file
        '''
        if filename.endswith('.gz'):
            with gzip.open(filename, 'rt', encoding='utf-8') as gzfile:
                return RawXML(gzfile.read())
        else:
            with codecs.open(filename, encoding='utf-8') as infile:
                return RawXML(infile.read())


class RawParse(object):
    ''' A raw parse (e.g. ACE MRS string) '''

    def __init__(self, node=None, mrs=None, dmrs=None):
        self.node = node  # reading node
        self.mrs = mrs  # from mrs string
        self.dmrs = dmrs  # from dmrs_xml_str

    def mrs_str(self):
        return etree.tostring(self.mrs).decode('utf-8') if self.mrs is not None else ''

    def dmrs_str(self):
        return etree.tostring(self.dmrs).decode('utf-8') if self.dmrs is not None else ''


def getSentenceFromFile(file_path):
    ''' Get sentence from either .xml file or .gz file '''
    raw = RawXML.from_file(file_path)  # supports both .xml file and .gz file now
    filename = os.path.basename(file_path)
    return getSentenceFromRawXML(raw, filename)


def getSentenceFromXMLString(xmlcontent):
    if isinstance(xmlcontent, etree._Element):
        raw = RawXML(xml=xmlcontent)
    else:
        raw = RawXML(raw=xmlcontent)
    return getSentenceFromRawXML(raw)


def getSentenceFromXML(xml_node):
    ''' etree node to Sentence object '''
    return getSentenceFromRawXML(RawXML(xml=xml_node))


def getSentenceFromRawXML(raw, filename=None):
    # Build Sentence object
    sid = raw.xml.attrib['id']
    text = raw.xml.find('text').text
    sentence = Sentence(ident=sid, text=text)
    if filename:
        sentence.filename = filename
    # read comments if available
    comment_tag = raw.xml.find('comment')
    if comment_tag is not None:
        sentence.comment = comment_tag.text
    # read shallow if available
    shallow_tag = raw.xml.find('shallow')
    if shallow_tag is not None and shallow_tag.text:
        shallow = TaggedSentence.from_json(json.loads(shallow_tag.text))
        sentence.shallow = shallow  # import tags
        for c in shallow.concepts:
            if c.flag == 'E':
                sentence.flag = Sentence.ERROR
    # import parses
    for idx, parse in enumerate(raw):
        reading = sentence.add()
        reading.rid = parse.node.attrib['id']
        reading.mode = parse.node.attrib['mode']
        if parse.mrs is not None:
            # add raw MRS
            reading.mrs(parse.mrs.text)
        if parse.dmrs is not None:
            reading.dmrs(parse.dmrs_str())
        # XXX: parse all synthetic trees
    return sentence
