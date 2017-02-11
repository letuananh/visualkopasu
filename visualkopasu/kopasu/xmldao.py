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
import lxml

from chirptext.leutile import FileTool
from visualkopasu.util import getLogger
from .util import getSentenceFromFile
from .util import getSubFolders
from .util import getFiles
from .util import is_valid_name

logger = getLogger('visko.dao')


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
        if not is_valid_name(corpus_name):
            raise Exception("Invalid corpus name (provided: {}".format(corpus_name))
        FileTool.create_dir(os.path.join(self.path, corpus_name))

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

    def copy_sentence(self, sent_path, sentid=None):
        if sentid is not None and (not is_valid_name(sentid)):
            raise Exception("Invalid sentenceID (provided: {}".format(sentid))
        fname = '{}.xml.gz'.format(sentid) if sentid else os.path.basename(sent_path)
        target = os.path.join(self.path, fname)
        shutil.copy2(sent_path, target)

    def save_sentence(self, xmlcontent, sentid, pretty_print=True):
        if not is_valid_name(sentid):
            raise Exception("Invalid sentenceID (provided: {})".format(sentid))
        sent_path = os.path.join(self.path, str(sentid) + '.xml.gz')
        print("Saving to {}".format(sent_path))
        with gzip.open(sent_path, 'wb') as output_file:
            if isinstance(xmlcontent, lxml.etree._Element):
                xmlcontent = lxml.etree.tostring(xmlcontent, pretty_print=pretty_print, encoding='utf-8')
            else:
                xmlcontent = xmlcontent.encode('utf-8')
            output_file.write(xmlcontent)

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
