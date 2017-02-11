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
import lxml
import logging

from django.template import Context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.context_processors import csrf

from coolisf.util import Grammar

from visualkopasu.util import getLogger
from visualkopasu.kopasu import Biblioteche, Biblioteca
from visualkopasu.kopasu.util import RawXML, getSentenceFromXML
from visualkopasu.kopasu.models import Document

########################################################################


logger = getLogger('visko2.ui', logging.DEBUG)  # level = INFO (default)


def getAllCollections():
    collections = Biblioteche.get_all()
    for collection in collections:
        corpora = None
        if os.path.isfile(collection.sqldao.db_path):
            # there is a collection with this name
            corpora = collection.sqldao.getCorpora()
            collection.corpora = corpora if corpora is not None else []
            logger.debug("corpora of {}: {} | {}".format(collection.name, corpora, collection.corpora))
            # get all available corpus inside
            for corpus in collection.corpora:
                corpus.path = collection.textdao.getCorpusDAO(corpus.name).path
                corpus.documents = collection.sqldao.getDocumentOfCorpus(corpus.ID)
                for doc in corpus.documents:
                    doc.corpus = corpus
    for col in collections:
        logger.debug(col.name, col.corpora)
    return collections


def get_bib(bibname):
    return Biblioteca(bibname)

##########################################################################
# MAIN
##########################################################################


def home(request):
    c = Context({"title": "Visual Kopasu 2.0",
                 "header": "Visual Kopasu 2.0",
                 "collections": getAllCollections()})
    c.update(csrf(request))
    return render(request, "visko2/home/index.html", c)


def dev(request):
    c = Context({"title": "Test Bed @ Visual Kopasu 2.0",
                 "header": "Visual Kopasu 2.0",
                 "collections": getAllCollections()})
    c.update(csrf(request))

    return render(request, "visko2/dev/index.html", c)


##########################################################################
# COOLISF
##########################################################################


def delviz(request):
    c = Context({"title": "Delphin-viz",
                 "header": "Visual Kopasu 2.0"})
    c.update(csrf(request))
    return render(request, "visko2/delviz/index.html", c)


# Maximum parses
RESULTS = (1, 5, 10, 20, 30, 40, 50, 100, 500)


def isf(request):
    c = Context({"title": "Integrated Semantic Framework",
                 "header": "Visual Kopasu 2.0"})
    input_results = int(request.POST.get('input_results', 5))
    if input_results not in RESULTS:
        input_results = 5
    sentence_text = request.POST.get('input_sentence', None)
    if sentence_text:
        logger.info("Parsing sentence: {} | Max results: {p}".format(sentence_text, p=input_results))
        sent = Grammar().txt2dmrs(sentence_text, parse_count=input_results)
        logger.debug("sent.text = " + sent.text)
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


def create_collection(request):
    bib_name = request.POST.get('collection_name', None)
    try:
        Biblioteche.create(bib_name)
    except:
        msg = "Cannot create biblioteca with name = {}".format(bib_name)
        logger.error(msg)
        messages.error(request, msg)
    return redirect('visko2:list_collection')


def create_corpus(request, collection_name):
    corpus_name = request.POST.get('corpus_name', None)
    bib = get_bib(collection_name)
    try:
        bib.create_corpus(corpus_name)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)
    except:
        msg = "Cannot create corpus with name = {}".format(corpus_name)
        logger.error(msg)
        messages.error(request, msg)
        return redirect('visko2:list_corpus', collection_name=collection_name)


def create_doc(request, collection_name, corpus_name):
    doc_name = request.POST.get('doc_name', None)
    bib = get_bib(collection_name)
    try:
        # create SQLite doc
        corpus = bib.sqldao.getCorpus(corpus_name)[0]
        bib.sqldao.saveDocument(Document(doc_name, corpusID=corpus.ID))
        # create XML doc
        cdao = bib.textdao.getCorpusDAO(corpus_name)
        cdao.create_doc(doc_name)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)
    except:
        msg = "Cannot create corpus with name = {}".format(corpus_name)
        logger.error(msg)
        messages.error(request, msg)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)


def create_sent(request, collection_name, corpus_name, doc_id):
    bib = get_bib(collection_name)
    # corpus = dao.getCorpus(corpus_name)[0]
    doc = bib.sqldao.getDocument(doc_id)
    input_results = int(request.POST.get('input_results', 5))
    if input_results not in RESULTS:
        input_results = 5
    sentence_text = request.POST.get('input_sentence', None)
    if not sentence_text:
        logger.error("Sentence text cannot be empty")
    else:        
        isent = Grammar().txt2dmrs(sentence_text, parse_count=input_results)
        xsent = isent.to_visko_xml()
        vsent = getSentenceFromXML(xsent)
        # save to doc
        vsent.documentID = doc.ID
        try:
            logger.debug("Visko sent: {} | length: {}".format(vsent, len(vsent)))
            bib.sqldao.saveSentence(vsent)
            # save XML
            docdao = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
            docdao.save_sentence(xsent, vsent.ID)
            return redirect('visko2:list_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=vsent.ID)
        except Exception as e:
            logger.error("Cannot save sentence. Error = {}".format(e))
    # default
    return redirect('visko2:list_sent', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id)


def reparse_sent(request, collection_name, corpus_name, doc_id, sent_id):
    input_results = int(request.POST.get('input_results', 0))
    if not input_results:
        logger.error("Invalid parse count (provided {})".format(input_results))
    else:
        dao = get_bib(collection_name).sqldao
        # corpus = dao.getCorpus(corpus_name)[0]
        # doc = dao.getDocument(doc_id)
        sent = dao.getSentence(sent_id)
        logger.debug("Reparse (parse count: {})=> Sent: {} | length: {}".format(input_results, sent, len(sent)))
    return redirect('visko2:list_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=sent_id)


def delete_sent(request, collection_name, corpus_name, doc_id, sent_id):
    bib = get_bib(collection_name)
    doc = bib.sqldao.getDocument(doc_id)
    try:
        bib.sqldao.delete_sent(sent_id)
        docdao = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
        docdao.delete_sent(sent_id)
    except Exception as e:
        logger.error("Cannot delete sentence. Error: {}".format(e))
    return redirect('visko2:list_sent', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id)


def list_collection(request):
    c = Context({"title": "Visual Kopasu 2.0",
                 "header": "Visual Kopasu 2.0",
                 "collections": getAllCollections()})
    c.update(csrf(request))
    return render(request, "visko2/corpus/index.html", c)


def list_corpus(request, collection_name):
    dao = get_bib(collection_name).sqldao
    corpora = dao.getCorpora()
    if corpora:
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
    dao = get_bib(collection_name).sqldao
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
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sentences = dao.getSentences(doc_id)
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus,
                 'doc': doc,
                 'sentences': sentences,
                 'input_results': 5,
                 'RESULTS': RESULTS})
    c.update(csrf(request))
    return render(request, "visko2/corpus/document.html", c)


def list_parse(request, collection_name, corpus_name, doc_id, sent_id):
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sent = dao.getSentence(sent_id)
    logger.debug("Sent: {} | length: {}".format(sent, len(sent)))
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus,
                 'doc': doc,
                 'sent': sent, 'sent_id': sent_id})
    # update reparse count
    input_results = RESULTS[-1]
    for r in RESULTS:
        if r < len(sent):
            continue
        input_results = r
        break
    c.update({'input_results': input_results, 'RESULTS': RESULTS})
    # retrieve original XML
    try:
        print("Has raw:", sent.has_raw())
        if sent is not None and sent.has_raw():
            # use built-in raws
            isfsent = sent.to_isf()
            print("ISF sent", isfsent)
            pass
        else:
            txtdao = get_bib(collection_name).textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
            raw = RawXML(txtdao.getSentenceRaw(sent.ident))
            isfsent = raw.to_isf()
        c.update({'sent': isfsent})
    except Exception as e:
        print("Error: {}".format(e))
        raise
        pass
    c.update(csrf(request))
    return render(request, "visko2/corpus/sentence.html", c)


def view_parse(request, collection_name, corpus_name, doc_id, sent_id, parse_id):
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sent = dao.getSentence(sent_id, interpretationIDs=(parse_id,))
    print("Sent: {} | parse_id: {} | length: {}".format(sent, parse_id, len(sent)))
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus,
                 'doc': doc,
                 'sent': sent, 'sent_id': sent_id})
    # update reparse count
    input_results = 5
    c.update({'input_results': input_results, 'RESULTS': RESULTS})
    # convert Visko Sentence into ISF to display
    isfsent = sent.to_isf()
    print(len(isfsent))
    c.update({'sent': isfsent, 'parse': isfsent[0]})
    c.update(csrf(request))
    return render(request, "visko2/corpus/parse.html", c)
