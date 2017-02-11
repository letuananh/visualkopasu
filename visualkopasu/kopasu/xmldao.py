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
from xml.etree import ElementTree as ETree

from chirptext.leutile import FileTool
from visualkopasu.util import getLogger
from .util import RawXML
from .util import getSentenceFromFile

logger = getLogger('visko.dao')


def getSubFolders(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isdir(os.path.join(a_folder, child))]


def getFiles(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isfile(os.path.join(a_folder, child))]


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

    def createCorpus(self, corpus_name):
        FileTool.create_dir(os.path.join(self.path, corpus_name))

    def getCorpora(self):
        ''' Get all available corpora
        '''
        return self.getSubFolders(self.path)


class XMLCorpusDAO:

    def __init__(self, path, name, collection=None):
        self.path = path
        self.name = name
        self.collection = collection

    def getDocumentDAO(self, doc_name):
        doc_path = os.path.join(self.path, doc_name)
        return XMLDocumentDAO(doc_path, doc_name)

    def create_doc(self, doc_name):
        FileTool.create_dir(os.path.join(self.path, doc_name))


class XMLDocumentDAO:

    def __init__(self, path, name, corpus=None):
        self.path = path
        self.name = name
        self.corpus = corpus

    def getSentences(self):
        all_files = [f.split('.')[0] for f in getFiles(self.path)]
        all_files.sort()
        return all_files

    def add_sentence(self, sent_path, sentid=None):
        fname = '{}.xml.gz'.format(sentid) if sentid else os.path.basename(sent_path)
        target = os.path.join(self.path, fname)
        shutil.copy2(sent_path, target)

    def delete_sent(self, sentenceID):
        file_path = self.getPath(sentenceID)
        if not file_path:
            raise Exception("Sentence {s} does not exist (path={p})".format(s=sentenceID, p=file_path))
        else:
            os.unlink(file_path)

    def getPath(self, sentenceID=None):
        if not sentenceID:
            raise Exception("sentenceID cannot be None")
        else:
            file_name = os.path.join(self.path, str(sentenceID) + '.xml.gz')
            file_name2 = os.path.join(self.path,
                                      "%s-%s.xml.gz" % (self.name, str(sentenceID)))
            logger.debug(("Filename1: %s" % file_name))
            logger.debug(("Filename2: %s" % file_name2))

            if os.path.isfile(file_name):
                return file_name
            elif os.path.isfile(file_name2):
                return file_name2
        return None

    def getSentenceRaw(self, sentenceID):
        # Parse the file
        full_path = self.getPath(sentenceID)
        logger.debug(full_path)
        with gzip.open(full_path, 'r') as gzfile:
            return gzfile.read()

    def getSentence(self, sentenceID):
        # Read raw text from file
        full_path = self.getPath(sentenceID)
        # Parse the file
        return getSentenceFromFile(full_path)
