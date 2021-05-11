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
import logging
from lxml import etree

from texttaglib.chirptext.leutile import FileHelper
from coolisf.util import is_valid_name
from coolisf.model import Document, Sentence

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
        return DocumentDAOXML(doc_path, doc_name)

    def create_doc(self, doc_name):
        if not is_valid_name(doc_name):
            raise Exception("Invalid doc name (provided: {}".format(doc_name))
        FileHelper.create_dir(os.path.join(self.path, doc_name))


class DocumentDAOXML(object):

    def __init__(self, path, name, corpus=None):
        self._path = FileHelper.abspath(path)
        self.name = name
        self.corpus = corpus

    @property
    def path(self):
        return self._path

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

    @property
    def archive_path(self):
        if self.path.endswith('/'):
            return self.path[:-1] + ".gz"
        else:
            return self.path + ".gz"

    def archive(self, doc):
        ''' Archive a doc to a gzip file in corpus folder '''
        with gzip.open(self.archive_path, 'wt') as archive_file:
            archive_file.write(doc.to_xml_str())

    def is_archived(self):
        return os.path.isfile(self.archive_path)

    def read_archive(self):
        ''' Open archive file and return a document object '''
        if os.path.isfile(self.archive_path):
            with gzip.open(self.archive_path, 'rt') as archive_file:
                return Document.from_xml_str(archive_file.read())
        return None

    def iter_archive(self, archive_path=None):
        if archive_path is None:
            archive_path = self.archive_path
        ''' Read sentence one at a time (recommended for large file) '''
        if os.path.isfile(archive_path):
            with gzip.open(archive_path, 'rb') as archive_file:
                for event, node in etree.iterparse(archive_file):
                    if event == 'end' and node.tag == 'sentence':
                        yield Sentence.from_xml_node(node)
                        node.clear()

    def save_sent(self, sent):
        sentid = str(sent.ID)
        if not is_valid_name(sentid):
            raise Exception("Invalid sentence ID (provided: {})".format(sentid))
        sent_path = os.path.join(self.path, str(sentid) + '.xml.gz')
        logging.info("Saving sentence to {}".format(sent_path))
        with gzip.open(sent_path, 'wt') as outfile:
            outfile.write(sent.to_xml_str())

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

    def get_sent(self, sentid):
        # Read raw text from file
        full_path = self.getPath(sentid)
        # Parse the file
        return Sentence.from_file(full_path)
