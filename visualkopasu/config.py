'''
Global config file for VisualKopasu
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

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2012, Visual Kopasu"
__credits__ = [ "Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying" ]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os
from visualkopasu.kopasu.xmldao import XMLBiblioteche
from visualkopasu.kopasu.dao import SQLiteCorpusCollection


class ViskoConfig:
    
    PROJECT_ROOT = os.path.expanduser('~/wk/visualkopasu')
    DJANGO_VIEW_DIR = os.path.join(PROJECT_ROOT, 'visualkopasu/visko_webui/views/')
    DJANGO_STATIC_DIR = os.path.join(PROJECT_ROOT, 'visualkopasu/visko_webui/static/')
    DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data')
    BIBLIOTECHE_ROOT = os.path.join(DATA_FOLDER, 'biblioteche')

    # available corpora
    AvailableBiblioteche = ('redwoods','test')
    TextCorpora = XMLBiblioteche(BIBLIOTECHE_ROOT)
    SqliteCorpora = SQLiteCorpusCollection(BIBLIOTECHE_ROOT)

    Biblioteche = []
    BibliotecheMap = {}
    # Setup scripts root
    SETUP_SCRIPTS_ROOT = os.path.join(PROJECT_ROOT, 'visualkopasu', 'console', 'scripts')

    # Django database - DO NOT CHANGE THIS!
    DATABASES_default_ENGINE = 'django.db.backends.sqlite3'
    DATABASES_default_NAME = os.path.join(PROJECT_ROOT, 'data/visko.db')


class Biblioteca:
    ''' One biblioteca contains many corpora
        It's a collection of documents
    '''

    def __init__(self, name, root=ViskoConfig.BIBLIOTECHE_ROOT):
        self.name = name
        self.root = root
        self.textdao = ViskoConfig.TextCorpora.getCorpusCollection(name)
        self.sqldao = ViskoConfig.SqliteCorpora.getCorpusDAO(name)
        self.corpora = []

    def get_sql_corpora(self):
        self.corpora = self.sqldao.getCorpora()
        for corpus in self.corpora:
            corpus.documents = self.sqldao.getDocumentOfCorpus(corpus.ID)
            for doc in corpus.documents:
                doc.corpus = corpus

# TODO: This should not be hardcoded
if not ViskoConfig.Biblioteche:
    for corpus in ViskoConfig.AvailableBiblioteche:
        cdao = Biblioteca(corpus)
        ViskoConfig.Biblioteche.append(cdao)
        ViskoConfig.BibliotecheMap[corpus] = cdao
