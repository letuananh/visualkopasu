# -*- coding: utf-8 -*-

'''
Visko 2.0 - Views
@author: Le Tuan Anh
'''

# Copyright 2017, Le Tuan Anh (tuananh.ke@gmail.com)
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

from lxml import etree

from django.template import Context
from django.shortcuts import render
from django.core.context_processors import csrf

from coolisf.util import Grammar

from visualkopasu.config import ViskoConfig as vkconfig
from visualkopasu.kopasu.util import RawXML

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
# DEV
##########################################################################


def dev(request):
    c = Context({"title": "Test Bed @ Visual Kopasu 2.0",
                 "header": "Visual Kopasu 2.0",
                 "collections": getAllCollections()})
    c.update(csrf(request))

    return render(request, "visko2/dev/index.html", c)


##########################################################################
# COOLISF
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


# Maximum parses
RESULTS = (1, 5, 10, 50, 100, 500)


def isf(request):
    c = Context({"title": "Integrated Semantic Framework",
                 "header": "Visual Kopasu 2.0"})
    input_results = int(request.POST.get('input_results', 5))
    if input_results not in RESULTS:
        input_results = 5
    sentence_text = request.POST.get('input_sentence', None)
    if sentence_text:
        print("Parsing sentence: {} | Max results: {p}".format(sentence_text, p=input_results))
        sent = Grammar().txt2dmrs(sentence_text, parse_count=input_results)
        print("sent.text = " + sent.text)
        c.update({'sent': sent})
    else:
        sentence_text = 'Three musketeers walk into a bar.'
    # -------
    # render
    c.update(csrf(request))
    c.update({'input_sentence': sentence_text,
              'input_results': input_results,
              'RESULTS': RESULTS})
    return render(request, "visko2/isf/index.html", c)

##########################################################################
# CORPUS
##########################################################################


def list_collection(request):
    c = Context({"title": "Visual Kopasu 2.0",
                 "header": "Visual Kopasu 2.0",
                 "collections": getAllCollections()})
    c.update(csrf(request))
    return render(request, "visko2/corpus/index.html", c)


def list_corpus(request, collection_name):
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    corpora = dao.getCorpora()
    for corpus in corpora:
        # fetch docs
            corpus.documents = dao.getDocumentOfCorpus(corpus.ID)
            for doc in corpus.documents:
                doc.corpus = corpus
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpora': corpora})
    c.update(csrf(request))
    return render(request, "visko2/corpus/collection.html", c)


def list_doc(request, collection_name, corpus_name):
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    corpus.documents = dao.getDocumentOfCorpus(corpus.ID)
    for doc in corpus.documents:
        doc.corpus = corpus
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus})
    c.update(csrf(request))
    return render(request, "visko2/corpus/corpus.html", c)


def list_sent(request, collection_name, corpus_name, doc_id):
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sentences = dao.getSentences(doc_id)
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus,
                 'doc': doc,
                 'sentences': sentences})
    c.update(csrf(request))
    return render(request, "visko2/corpus/document.html", c)


def list_parse(request, collection_name, corpus_name, doc_id, sent_id):
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sent = dao.getSentence(sent_id)
    # retrieve raw XML
    txtdao = vkconfig.BibliotecheMap[collection_name].textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
    raw = RawXML(txtdao.getSentenceRaw(sent.ident))
    isfsent = raw.to_isf()
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus,
                 'doc': doc,
                 'sentence': sent,
                 'raw': raw,
                 'isfsent': isfsent})
    c.update(csrf(request))
    return render(request, "visko2/corpus/sentence.html", c)
