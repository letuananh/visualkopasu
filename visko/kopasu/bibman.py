'''
Data access layer for VisualKopasu project.
@author: Le Tuan Anh
'''

# Copyright 2016, Le Tuan Anh (tuananh.ke@gmail.com)
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

########################################################################

import logging

from chirptext.leutile import FileHelper
from coolisf.util import is_valid_name

from visko.config import ViskoConfig as vkconfig
from visko.util import getFiles
from .dao import CorpusCollectionSQLite
from .xmldao import XMLBiblioteche


########################################################################

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2017, Visual Kopasu"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

logger = logging.getLogger(__name__)


class Biblioteche:

    @staticmethod
    def list_all(bibroot=vkconfig.BIBLIOTECHE_ROOT):
        return sorted([x.split('.')[0] for x in getFiles(bibroot) if x.endswith('.db')])

    @staticmethod
    def get_all(bibroot=vkconfig.BIBLIOTECHE_ROOT):
        return [Biblioteca(x, root=bibroot) for x in Biblioteche.list_all(bibroot)]

    @staticmethod
    def create(bibname, bibroot=vkconfig.BIBLIOTECHE_ROOT):
        if not is_valid_name(bibname):
            raise Exception("Invalid biblioteca name (provided: {}".format(bibname))
        bib = Biblioteca(bibname, root=bibroot)
        # create collection dir if needed
        FileHelper.create_dir(bib.textdao.path)
        # prepare DB
        bib.sqldao.corpus.select()


class Biblioteca:
    ''' One biblioteca contains many corpora
        It's a collection of documents
    '''

    def __init__(self, name, root=vkconfig.BIBLIOTECHE_ROOT):
        self.name = name
        self.root = root
        self.textdao = XMLBiblioteche(root).getCorpusCollection(name)
        self.sqldao = CorpusCollectionSQLite(root).getCorpusDAO(name)
        self.corpora = []

    def create_corpus(self, corpus_name):
        self.sqldao.create_corpus(corpus_name)
        self.textdao.create_corpus(corpus_name)

    def get_sql_corpora(self):
        self.corpora = self.sqldao.getCorpora()
        for corpus in self.corpora:
            corpus.documents = self.sqldao.get_docs(corpus.ID)
            for doc in corpus.documents:
                doc.corpus = corpus
