"""
Data access layer for VisualKopasu project.
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

import logging

from texttaglib.chirptext.leutile import FileHelper
from coolisf.util import is_valid_name

from visko.config import ViskoConfig as vkconfig
from visko.util import getFiles
from .dao import CorpusCollectionSQLite
from .xmldao import XMLBiblioteche


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
    """ One biblioteca contains many corpora
        It's a collection of documents
    """

    def __init__(self, name, root=vkconfig.BIBLIOTECHE_ROOT):
        self.name = name
        self.root = root
        self.textdao = XMLBiblioteche(root).getCorpusCollection(name)
        self.sqldao = CorpusCollectionSQLite(root).getCorpusDAO(name)
        self.corpuses = []

    def create_corpus(self, corpus_name):
        self.sqldao.create_corpus(corpus_name)
        self.textdao.create_corpus(corpus_name)

    def get_corpuses(self):
        with self.sqldao.ctx() as ctx:
            self.corpuses = ctx.corpus.select()
            for corpus in self.corpuses:
                corpus.documents = self.sqldao.get_docs(corpus.ID, ctx=ctx)
                for doc in corpus.documents:
                    doc.corpus = corpus
                    q = "SELECT COUNT(*) FROM sentence WHERE docID = ?"
                    p = (doc.ID,)
                    doc.sent_count = ctx.select_scalar(q, p)
        return self.corpuses

    def get_corpus_info(self, corpus, ctx=None):
        if ctx is None:
            with self.sqldao.ctx() as ctx:
                return self.get_corpus_info(corpus, ctx=ctx)
        # context is ensured
        corpus.documents = self.sqldao.get_docs(corpus.ID, ctx=ctx)
        for doc in corpus.documents:
            doc.corpus = corpus
            q = "SELECT COUNT(*) FROM sentence WHERE docID = ?"
            p = (doc.ID,)
            doc.sent_count = ctx.select_scalar(q, p)
        return corpus
