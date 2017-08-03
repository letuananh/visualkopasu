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
import logging
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse

from chirptext.texttaglib import TagInfo
from coolisf.util import GrammarHub, sent2json

from djangoisf.views import jsonp, TAGGERS
from visko.util import getLogger
from visko.kopasu import Biblioteche, Biblioteca
from visko.kopasu.xmldao import getSentenceFromXML, getDMRSFromXML
from visko.kopasu.util import dmrs_str_to_xml, xml_to_str
from visko.kopasu.models import Document, ParseRaw, Reading, Sentence
from visko.kopasu.dmrs_search import LiteSearchEngine


########################################################################

logger = getLogger('visko2.ui', logging.DEBUG)  # level = INFO (default)
SEARCH_LIMIT = 10000

# TODO: Make this more flexible
# Maximum parse count
RESULTS = (1, 5, 10, 20, 30, 40, 50, 100, 500)
ghub = GrammarHub()
PROCESSORS = ghub.available
PROCESSORS.update({'': 'None'})
ISF_DEFAULT = {'input_results': 5, 'RESULTS': RESULTS,
               'PROCESSORS': PROCESSORS, 'input_parser': 'ERG',
               'input_tagger': TagInfo.LELESK, 'TAGGERS': TAGGERS,
               'input_sentence': "Abrahams' dogs barked."}


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
        logger.debug("{n} - {c}".format(n=col.name, c=col.corpora))
    return collections


def get_bib(bibname):
    return Biblioteca(bibname)


def get_context(extra=None, title=None):
    c = {"title": "Visual Kopasu 2.0",
         "header": "Visual Kopasu 2.0"}
    if extra:
        c.update(extra)
    if title:
        c['title'] = title
    return c


##########################################################################
# MAIN
##########################################################################


def home(request):
    c = get_context(ISF_DEFAULT)
    c['collections'] = getAllCollections()
    return render(request, "visko2/home/index.html", c)


@csrf_protect
def dev(request, mode=None):
    c = get_context({"title": "Test Bed @ Visual Kopasu 2.0",
                     "collections": getAllCollections()})
    if mode == 'isf':
        return render(request, "visko2/dev/isf.html", c)
    elif mode == 'vk2':
        return render(request, "visko2/dev/visko2.html", c)
    else:
        return render(request, "visko2/dev/index.html", c)


@jsonp
@csrf_protect
def dev_rest(request):
    input = request.POST.get('input', '')
    return {'input': input, 'output': input[::-1]}


##########################################################################
# COOLISF
##########################################################################


def delviz(request):
    c = get_context(title="Delphin-viz")
    return render(request, "visko2/delviz/index.html", c)


def isf(request):
    c = get_context(ISF_DEFAULT, title="CoolISF REST Client")
    if request.method == 'POST':
        input_sentence = request.POST.get('input_sentence')
        input_parser = request.POST.get('input_parser')
        input_tagger = request.POST.get('input_tagger')
        input_results = int(request.POST.get('input_results'))
        c.update({'input_sentence': input_sentence,
                  'input_parser': input_parser,
                  'input_tagger': input_tagger,
                  'input_results': input_results})
    print(c)
    return render(request, "visko2/isf/index.html", c)


def yawol(request):
    c = get_context(ISF_DEFAULT, title="Yawol REST Client")
    return render(request, "visko2/yawol/index.html", c)


##########################################################################
# SEARCH
##########################################################################

def search(request, sid=None):
    cols = getAllCollections()
    c = get_context({'collections': cols}, title='Search')
    if request.method == 'GET':
        c.update({'sentences': []})
    elif request.method == 'POST':
        query = request.POST.get('query', '')
        col = request.POST.get('col', '')
        c.update({'query': query, 'col': col})
        logger.info('Col: {c} - Query: {q}'.format(c=col, q=query))
        if query:
            if col:
                # search in specified collection
                bib = Biblioteca(col)
                engine = LiteSearchEngine(bib.sqldao, limit=SEARCH_LIMIT)
                # TODO: reuse engine objects
                sentences = engine.search(query)
                for s in sentences:
                    s.collection = col
                c.update({'sentences': sentences})
                logger.info('Col: {c} - Query: {q} - Results: {r}'.format(c=col, q=query, r=sentences))
            else:
                # search in all collection
                sentences = []
                for bib in cols:
                    engine = LiteSearchEngine(bib.sqldao, limit=SEARCH_LIMIT)
                    sents = engine.search(query)
                    for s in sents:
                        s.collection = bib.name
                    sentences += sents
                c.update({'sentences': sentences})
    return render(request, "visko2/corpus/search.html", c)


##########################################################################
# CORPUS MANAGEMENT
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
    doc_title = request.POST.get('doc_title', '')

    bib = get_bib(collection_name)
    try:
        # create SQLite doc
        corpus = bib.sqldao.getCorpus(corpus_name)[0]
        bib.sqldao.saveDocument(Document(doc_name, corpusID=corpus.ID, title=doc_title))
        # create XML doc
        cdao = bib.textdao.getCorpusDAO(corpus_name)
        cdao.create_doc(doc_name)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)
    except Exception as e:
        msg = "Cannot create document with name = {}".format(doc_name)
        logger.exception(e, msg)
        messages.error(request, msg)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)


def create_sent(request, collection_name, corpus_name, doc_id):
    bib = get_bib(collection_name)
    # corpus = dao.getCorpus(corpus_name)[0]
    doc = bib.sqldao.getDocument(doc_id)
    input_results = int(request.POST.get('input_results', 5))
    if input_results not in RESULTS:
        input_results = 5
    input_parser = request.POST.get('input_parser')
    if input_parser not in PROCESSORS:
        raise Http404("Invalid grammar")
    input_tagger = request.POST.get('input_tagger')
    sentence_text = request.POST.get('input_sentence', None)
    if not sentence_text:
        messages.error(request, "Sentence text cannot be empty")
    else:
        # parse the sentence
        if input_parser == '':
            # Just create a sentence with no parse
            s = Sentence(text=sentence_text)
            s.documentID = doc.ID
            bib.sqldao.saveSentence(s)
        elif input_parser in PROCESSORS:
            isent = ghub.parse(sentence_text, input_parser, pc=input_results, tagger=input_tagger)
            xsent = isent.tag_xml().to_visko_xml()
            vsent = getSentenceFromXML(xsent)
            # save to doc
            vsent.documentID = doc.ID
            try:
                logger.debug("Visko sent: {} | length: {}".format(vsent, len(vsent)))
                bib.sqldao.saveSentence(vsent)
                # save XML
                docdao = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
                docdao.save_sentence(xsent, vsent.ID)
                # if everything went right, save config
                doc.grammar = input_parser
                doc.tagger = input_tagger
                doc.parse_count = input_results
                bib.sqldao.saveDocument(doc)
                return redirect('visko2:list_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=vsent.ID)
            except Exception as e:
                logger.error("Cannot save sentence. Error = {}".format(e))
        else:
            raise Http404("Invalid grammar has been selected")
    # default
    return redirect('visko2:list_sent', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id)


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


@csrf_protect
def list_collection(request):
    c = get_context({"collections": getAllCollections()})
    return render(request, "visko2/corpus/index.html", c)


@csrf_protect
def list_corpus(request, collection_name):
    dao = get_bib(collection_name).sqldao
    corpora = dao.getCorpora()
    if corpora:
        for corpus in corpora:
            # fetch docs
                corpus.documents = dao.getDocumentOfCorpus(corpus.ID)
                for doc in corpus.documents:
                    doc.corpus = corpus
    c = get_context({'title': 'Corpus',
                              'collection_name': collection_name,
                              'corpora': corpora})
    return render(request, "visko2/corpus/collection.html", c)


@csrf_protect
def list_doc(request, collection_name, corpus_name):
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    corpus.documents = dao.getDocumentOfCorpus(corpus.ID)
    for doc in corpus.documents:
        doc.corpus = corpus
    c = get_context({'title': 'Corpus ' + corpus_name,
                     'collection_name': collection_name,
                     'corpus': corpus})
    return render(request, "visko2/corpus/corpus.html", c)


@csrf_protect
def list_sent(request, collection_name, corpus_name, doc_id, input_results=5, input_parser='ERG'):
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sentences = dao.getSentences(doc_id)
    c = get_context({'collection_name': collection_name,
                     'corpus': corpus,
                     'doc': doc,
                     'sentences': sentences},
                    title='Document: ' + doc.title if doc.title else doc.name)
    c.update(ISF_DEFAULT)
    print(doc)
    if doc.grammar and doc.grammar in PROCESSORS:
        c['input_parser'] = doc.grammar
    if doc.tagger and doc.tagger in TAGGERS:
        c['input_tagger'] = doc.tagger
    if doc.parse_count and doc.parse_count in RESULTS:
        c['input_results'] = doc.parse_count
    return render(request, "visko2/corpus/document.html", c)


def list_parse(request, collection_name, corpus_name, doc_id, sent_id):
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sent = dao.getSentence(sent_id)
    # sent.ID = sent_id
    # if len(sent) == 1:
    #     # redirect to first parse to edit quicker
    #     return redirect('visko2:view_parse', col_name=collection_name, cor=corpus_name, did=doc_id, sid=sent_id, pid=sent[0].ID)
    c = get_context({'title': 'Sentence: ' + sent.text,
                     'col': collection_name,
                     'corpus': corpus,
                     'doc': doc,
                     'sid': sent_id})
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
        c.update({'sent': sent.to_isf()})
    except Exception as e:
        print("Error: {}".format(e))
        raise
        pass
    return render(request, "visko2/corpus/sentence.html", c)


@csrf_protect
def view_parse(request, col, cor, did, sid, pid):
    dao = get_bib(col).sqldao
    corpus = dao.getCorpus(cor)[0]
    doc = dao.getDocument(did)
    sent = dao.getSentence(sid, readingIDs=(pid,))
    c = get_context({'title': 'Sentence: ' + sent.text,
                     'col': col,
                     'corpus': corpus,
                     'doc': doc,
                     'sid': sid,
                     'pid': pid})
    # convert Visko Sentence into ISF to display
    isfsent = sent.to_isf()
    c.update({'sent': isfsent, 'parse': isfsent[0], 'vdmrs': sent[0].dmrs[0]})
    return render(request, "visko2/corpus/parse.html", c)


##########################################################################
# REST APIs
##########################################################################

@jsonp
def rest_fetch(request, col, cor, did, sid, pid=None):
    dao = get_bib(col).sqldao
    if pid:
        sent = dao.getSentence(sid, readingIDs=(pid,)).to_isf()
    else:
        sent = dao.getSentence(sid).to_isf()
    return sent2json(sent)


@csrf_protect
@jsonp
def rest_dmrs_parse(request, col, cor, did, sid, pid):
    dao = get_bib(col).sqldao
    # corpus = dao.getCorpus(cor)[0]
    # doc = dao.getDocument(did)
    sent = dao.getSentence(sid, readingIDs=(pid,))
    dmrs_raw = request.POST.get('dmrs', '')
    dmrs_xml = dmrs_str_to_xml(dmrs_raw)
    dmrs = getDMRSFromXML(dmrs_xml)
    sent.mode = Reading.ACTIVE
    sent.readings[0].dmrs = [dmrs]
    sent.readings[0].raws = [ParseRaw(xml_to_str(dmrs_xml), rtype=ParseRaw.XML)]
    return sent2json(sent.to_isf())


@csrf_protect
@jsonp
def rest_dmrs_save(request, action, col, cor, did, sid, pid):
    if action not in ('insert', 'replace'):
        raise Exception("Invalid action provided")
    dao = get_bib(col).sqldao
    # corpus = dao.getCorpus(cor)[0]
    doc = dao.getDocument(did)
    sent = dao.getSentence(sid, readingIDs=(pid,))

    # Parse given DMRS
    dmrs_raw = request.POST.get('dmrs', '')
    dmrs_xml = dmrs_str_to_xml(dmrs_raw)
    dmrs = getDMRSFromXML(dmrs_xml)
    sent.mode = Reading.ACTIVE
    sent.readings[0].dmrs = [dmrs]
    sent.readings[0].raws = [ParseRaw(xml_to_str(dmrs_xml), rtype=ParseRaw.XML)]
    try:
        sent2json(sent.to_isf())
    except Exception as e:
        logger.exception("DMRS string is not well-formed")
        raise e

    if action == 'replace':
        # this will replace old (existing) DMRS
        dao.deleteReading(pid)
        # assign a new ident to this new parse
    sentinfo = dao.getSentence(sent.ID, skip_details=True, get_raw=False)
    new_parse = Reading(rid='{}-manual'.format(len(sentinfo)), mode=Reading.ACTIVE)
    new_parse.sentenceID = sent.ID
    new_parse.dmrs.append(dmrs)
    new_parse.raws = [ParseRaw(xml_to_str(dmrs_xml), rtype=ParseRaw.XML)]
    dao.saveReading(new_parse, doc.ID)
    if new_parse.ID:
        # complete
        return {"success": True, "url": reverse('visko2:view_parse', args=[col, cor, did, sid, new_parse.ID])}
    else:
        raise Exception("Error occurred while creating reading")


@csrf_protect
@jsonp
def rest_dmrs_delete(request, col, cor, did, sid, pid):
    dao = get_bib(col).sqldao
    try:
        dao.deleteReading(pid)
        return {"success": True, "url": reverse('visko2:list_parse', args=[col, cor, did, sid])}
    except Exception as e:
        logger.exception("Cannot delete parse ID={}".format(pid))
        raise e
