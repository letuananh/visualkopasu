# -*- coding: utf-8 -*-

'''
Visko 2.0 - Views
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
# along with VisualKopasu. If not, see http://www.gnu.org/licenses/

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2017, Visual Kopasu"
__credits__ = ["Francis Bond"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################


import os

from django.template import Context
from django.shortcuts import render
from django.core.context_processors import csrf

from visualkopasu.config import ViskoConfig as vkconfig


########################################################################


def getAllCollections():
    for collection in vkconfig.Biblioteche:
        corpora = None
        if os.path.isfile(collection.sqldao.db_path):
            corpora = collection.sqldao.getCorpora()
        collection.corpora = corpora if corpora else []
        for corpus in collection.corpora:
            corpus.path = collection.textdao.getCorpusDAO(corpus.name).path
            corpus.documents = collection.sqldao.getDocumentOfCorpus(corpus.ID)
            for doc in corpus.documents:
                doc.corpus = corpus
    return vkconfig.Biblioteche


##########################################################################
# VIEWS
##########################################################################


def home(request):
    c = Context({"title": "Visual Kopasu 2.0",
                 "header": "Visual Kopasu 2.0",
                 "collections": getAllCollections()})
    c.update(csrf(request))
    return render(request, "visko2/home/index.html", c)


def delviz(request):
    c = Context({"title": "Delphin-viz",
                 "header": "Visual Kopasu 2.0"})
    c.update(csrf(request))
    return render(request, "visko2/delviz/index.html", c)
