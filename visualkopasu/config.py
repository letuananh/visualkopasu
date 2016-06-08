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
from visualkopasu.kopasu.dao import DocumentDAO 

class VisualKopasuConfiguration:
    PROJECT_ROOT = os.path.expanduser('~/wk/visualkopasu')
    DJANGO_VIEW_DIR = os.path.join(PROJECT_ROOT, 'visualkopasu/visko_webui/views/')
    DJANGO_STATIC_DIR = os.path.join(PROJECT_ROOT, 'visualkopasu/visko_webui/static/')
    CORPORA_FOLDER = os.path.join(PROJECT_ROOT, 'data/corpora')

    # Default corpus
    CORPUS = 'redwoods' 
    DEFAULT_DB_NAME = "redwoods"

    ACL_CORPORA_ROOT = os.path.join(CORPORA_FOLDER, 'acl')
    ACL_DB_NAME = 'acl' # without .db extension


    # Setup scripts root
    SETUP_SCRIPTS_ROOT = os.path.join(PROJECT_ROOT, 'visualkopasu', 'console', 'scripts')

    # Django database - DO NOT CHANGE THIS!
    DATABASES_default_ENGINE = 'django.db.backends.sqlite3'
    DATABASES_default_NAME = os.path.join(PROJECT_ROOT, 'data/visko.db')

    @staticmethod
    def buildDAO(dbname=None):
        root = VisualKopasuConfiguration.CORPORA_FOLDER
        corpus = VisualKopasuConfiguration.CORPUS
        dbname = VisualKopasuConfiguration.DEFAULT_DB_NAME if dbname is None else dbname
        dao = DocumentDAO.getDAO(DocumentDAO.SQLITE3, {'root': root, 'corpus': corpus, 'dbname': dbname, 'fill_cache' : False })    
        print("Connecting to DB: %s" % dao.orm_manager.db_path)
        return dao

    @staticmethod
    def buildTextDAO(dbname=None,documentID=''):
        root = VisualKopasuConfiguration.CORPORA_FOLDER
        corpus = VisualKopasuConfiguration.CORPUS
        dbname = VisualKopasuConfiguration.DEFAULT_DB_NAME + ".zip" if dbname is None else dbname + ".zip"
        dao = DocumentDAO.getDAO(DocumentDAO.XML, { 'root': root, 'corpus': corpus, 'dbname': dbname, 'document': documentID})
        print("Connecting to DB: %s" % dao.getPath())
        return dao

    DAO = None
    SQLDAOs = None

    @staticmethod
    def initDAO():
        if VisualKopasuConfiguration.DAO is None:
            VisualKopasuConfiguration.DAO = { 
                VisualKopasuConfiguration.DEFAULT_DB_NAME : { 'sql' : VisualKopasuConfiguration.buildDAO()
                                            , 'text' : VisualKopasuConfiguration.buildTextDAO()
                                                } 
                }
            VisualKopasuConfiguration.SQLDAOs = [item['sql'] for item in VisualKopasuConfiguration.DAO.values()]
    @staticmethod
    def getDAO(dbname=None):
        dbname = VisualKopasuConfiguration.DEFAULT_DB_NAME if dbname is None else dbname
        return VisualKopasuConfiguration.DAO[dbname]['sql']
    @staticmethod
    def getTextDAO(dbname=None):
        dbname = VisualKopasuConfiguration.DEFAULT_DB_NAME if dbname is None else dbname
        return VisualKopasuConfiguration.DAO[dbname]['text']
        
VisualKopasuConfiguration.initDAO()
