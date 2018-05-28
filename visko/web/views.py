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

from chirptext.cli import setup_logging
from chirptext import texttaglib as ttl
from coolisf import GrammarHub
from coolisf.util import sent2json
from coolisf.morph import Transformer
from coolisf.model import Document, Reading, Sentence

from djangoisf.views import jsonp, TAGGERS
from visko.kopasu import Biblioteche, Biblioteca
from visko.util import Paginator
from visko.kopasu.dmrs_search import LiteSearchEngine


########################################################################

SEARCH_LIMIT = 10000

# TODO: Make this more flexible
# Maximum parse count
RESULTS = (1, 5, 10, 20, 30, 40, 50, 100, 500)
PAGESIZE = 1000
ghub = GrammarHub()
PROCESSORS = ghub.available
PROCESSORS.update({'': 'None'})
ISF_DEFAULT = {'input_results': 5, 'RESULTS': RESULTS,
               'PROCESSORS': PROCESSORS, 'input_parser': 'ERG_ISF',
               'input_tagger': ttl.Tag.LELESK, 'TAGGERS': TAGGERS,
               'input_sentence': "Abrahams' dogs barked."}
SENT_FLAGS = [{'value': str(Sentence.NONE), 'text': 'None'},
              {'value': str(Sentence.GOLD), 'text': 'Gold'},
              {'value': str(Sentence.ERROR), 'text': 'Error'},
              {'value': str(Sentence.WARNING), 'text': 'Warning'}]
SENT_FLAG_MAP = {i['value']: i['text'] for i in SENT_FLAGS}
# Setup logging
setup_logging('logging.json', 'logs')


def getLogger():
    return logging.getLogger(__name__)


def getAllCollections():
    collections = Biblioteche.get_all()
    for collection in collections:
        if os.path.isfile(collection.sqldao.db_path):
            collection.get_corpuses()
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


def isf(request, col=None, sid=None):
    c = get_context(ISF_DEFAULT, title="CoolISF REST Client")
    if request.method == 'GET' and col and sid:
        dao = get_bib(col).sqldao
        sent = dao.get_sent(sid)
        c.update({'input_sentence': sent.text})
    if request.method == 'POST':
        input_sentence = request.POST.get('input_sentence')
        input_parser = request.POST.get('input_parser')
        input_tagger = request.POST.get('input_tagger')
        input_results = int(request.POST.get('input_results'))
        c.update({'input_sentence': input_sentence,
                  'input_parser': input_parser,
                  'input_tagger': input_tagger,
                  'input_results': input_results})
    return render(request, "visko2/isf/index.html", c)


def isf_editor(request):
    c = get_context(ISF_DEFAULT, title="ISF - DMRS Editor")
    if request.method == 'POST':
        input_sentence = request.POST.get('input_sentence')
        input_parser = request.POST.get('input_parser')
        input_tagger = request.POST.get('input_tagger')
        input_results = int(request.POST.get('input_results'))
        c.update({'input_sentence': input_sentence,
                  'input_parser': input_parser,
                  'input_tagger': input_tagger,
                  'input_results': input_results})
    return render(request, "visko2/isf/editor.html", c)


def yawol(request):
    c = get_context(ISF_DEFAULT, title="Yawol REST Client")
    return render(request, "visko2/yawol/index.html", c)


##########################################################################
# SEARCH
##########################################################################

def search(request, sid=None):
    cols = getAllCollections()
    c = get_context({'collections': cols}, title='Search')
    sentences = None
    if request.method == 'GET':
        c.update({'sentences': []})
    elif request.method == 'POST':
        query = request.POST.get('query', '')
        col_name = request.POST.get('col', '')
        c.update({'query': query, 'col': col_name})
        getLogger().info('Col: {c} - Query: {q}'.format(c=col_name, q=query))
        if query:
            if col_name:
                # search in specified collection
                bib = Biblioteca(col_name)
                engine = LiteSearchEngine(bib.sqldao, limit=SEARCH_LIMIT)
                # TODO: reuse engine objects
                try:
                    sentences = engine.search(query)
                    for s in sentences:
                        s.collection = bib
                    c.update({'sentences': sentences})
                    getLogger().info('Col: {c} - Query: {q} - Results: {r}'.format(c=col_name, q=query, r=sentences))
                except:
                    getLogger().exception("Could not perform search with query: {}".format(query))
                    messages.error(request, "Could not process query (provided: `{}')".format(query))
            else:
                try:
                    # search in all collection
                    sentences = []
                    for bib in cols:
                        engine = LiteSearchEngine(bib.sqldao, limit=SEARCH_LIMIT)
                        sents = engine.search(query)
                        for s in sents:
                            s.collection = bib
                        sentences += sents
                    c.update({'sentences': sentences})
                except:
                    getLogger().exception("Could not perform search with query: {}".format(query))
                    messages.error(request, "Could not process query (provided: `{}')".format(query))
        # if sentences:
        #     for s in sentences:
        #         print(s, [r.ID for r in s])
        else:
            messages.warning(request, "Found nothing for given query: `{}'".format(query))
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
        getLogger().error(msg)
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
        getLogger().error(msg)
        messages.error(request, msg)
        return redirect('visko2:list_corpus', collection_name=collection_name)


def create_doc(request, collection_name, corpus_name):
    doc_name = request.POST.get('doc_name', None)
    doc_title = request.POST.get('doc_title', '')

    bib = get_bib(collection_name)
    try:
        # create SQLite doc
        corpus = bib.sqldao.get_corpus(corpus_name)
        bib.sqldao.save_doc(Document(doc_name, corpusID=corpus.ID, title=doc_title))
        # create XML doc
        cdao = bib.textdao.getCorpusDAO(corpus_name)
        cdao.create_doc(doc_name)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)
    except Exception as e:
        msg = "Cannot create document with name = {}".format(doc_name)
        getLogger().exception(e, msg)
        messages.error(request, msg)
        return redirect('visko2:list_doc', collection_name=collection_name, corpus_name=corpus_name)


def create_sent(request, collection_name, corpus_name, doc_id):
    bib = get_bib(collection_name)
    doc = bib.sqldao.doc.by_id(doc_id)
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
            s.docID = doc.ID
            bib.sqldao.save_sent(s)
        elif input_parser in PROCESSORS:
            sent = ghub.parse(sentence_text, input_parser, pc=input_results, tagger=input_tagger)
            sent.docID = doc.ID
            try:
                getLogger().debug("Result: {} | length: {}".format(sent, len(sent)))
                bib.sqldao.save_sent(sent)
                # [TODO] Save XML
                # docdao = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
                # docdao.save_sentence(xsent, vsent.ID)
                # if everything went right, save config
                doc.grammar = input_parser
                doc.tagger = input_tagger
                doc.parse_count = input_results
                bib.sqldao.save_doc(doc)
                return redirect('visko2:list_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=sent.ID)
            except Exception as e:
                getLogger().error("Cannot save sentence. Error = {}".format(e))
        else:
            raise Http404("Invalid grammar has been selected")
    # default
    return redirect('visko2:list_sent', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id)


def delete_sent(request, collection_name, corpus_name, doc_id, sent_id):
    bib = get_bib(collection_name)
    doc = bib.sqldao.doc.by_id(doc_id)
    try:
        bib.sqldao.delete_sent(sent_id)
        docdao = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc.name)
        docdao.delete_sent(sent_id)
    except Exception as e:
        getLogger().error("Cannot delete sentence. Error: {}".format(e))
    return redirect('visko2:list_sent', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id)


@csrf_protect
def list_collection(request):
    c = get_context({"collections": getAllCollections()})
    return render(request, "visko2/corpus/index.html", c)


@csrf_protect
def list_corpus(request, collection_name):
    bib = get_bib(collection_name)
    bib.get_corpuses()
    # for cor in bib.corpuses:
    #     print(cor.documents)
    c = get_context({'title': 'Corpus',
                              'collection_name': collection_name,
                              'corpuses': bib.corpuses})
    return render(request, "visko2/corpus/collection.html", c)


@csrf_protect
def list_doc(request, collection_name, corpus_name):
    bib = get_bib(collection_name)
    corpus = bib.sqldao.get_corpus(corpus_name)
    bib.get_corpus_info(corpus)  # get documents, sentence count, etc.
    c = get_context({'title': 'Corpus ' + corpus_name,
                     'collection_name': collection_name,
                     'corpus': corpus})
    return render(request, "visko2/corpus/corpus.html", c)


@csrf_protect
def list_sent(request, collection_name, corpus_name, doc_id, flag=None, input_results=5, input_parser='ERG'):
    page = int(request.GET.get('page', 0))
    pane = int(request.GET.get('pane', 8))
    dao = get_bib(collection_name).sqldao
    with dao.ctx() as ctx:
        doc_name = ctx.document.by_id(doc_id).name
        doc = dao.get_doc(doc_name, ctx=ctx)
        if corpus_name != doc.corpus.name:
            raise Exception("Invalid document name")
        pager = Paginator(pagesize=PAGESIZE, windowpane=pane)
        total = pager.total(doc.sent_count)
        if page > total:
            page = total
        pagination = pager.paginate(page, total)
        sentences = dao.get_sents(doc.ID, flag=flag, page=page, pagesize=pager.pagesize, ctx=ctx)
        sc = min(doc.sent_count - page * pager.pagesize, pager.pagesize, len(sentences))  # sentence count
    title = 'Document: {t} | Sentences: {total} (This page: {sc})'.format(t=doc.title if doc.title else doc.name, total=doc.sent_count, sc=sc)
    c = get_context({'col': collection_name,
                     'corpus': doc.corpus,
                     'doc': doc,
                     'flag': flag,
                     'sentences': sentences,
                     'pagination': pagination if total > 1 else None},
                    title=title)
    c.update(ISF_DEFAULT)
    if doc.grammar and doc.grammar in PROCESSORS:
        c['input_parser'] = doc.grammar
    if doc.tagger and doc.tagger in TAGGERS:
        c['input_tagger'] = doc.tagger
    if doc.parse_count and doc.parse_count in RESULTS:
        c['input_results'] = doc.parse_count
    return render(request, "visko2/corpus/document.html", c)


def list_parse(request, collection_name, corpus_name, doc_id, sent_id, flag=None):
    dao = get_bib(collection_name).sqldao
    with dao.ctx() as ctx:
        corpus = dao.get_corpus(corpus_name)
        doc = dao.doc.by_id(doc_id)
        sent = dao.get_sent(sent_id)
        next_sid = dao.next_sentid(sent.ID, flag, ctx=ctx)
        prev_sid = dao.prev_sentid(sent.ID, flag, ctx=ctx)
    # sent.ID = sent_id
    # if len(sent) == 1:
    #     # redirect to first parse to edit quicker
    #     return redirect('visko2:view_parse', col_name=collection_name, cor=corpus_name, did=doc_id, sid=sent_id, pid=sent[0].ID)
    c = get_context({'title': 'Sentence: ' + sent.text,
                     'col': collection_name,
                     'corpus': corpus,
                     'doc': doc,
                     'sid': sent_id, 'sent_ident': sent.ident,
                     'next_sid': next_sid,
                     'prev_sid': prev_sid,
                     'flag': flag})
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
        c.update({'sent': sent})
    except Exception as e:
        raise
    return render(request, "visko2/corpus/sentence.html", c)


@csrf_protect
def view_parse(request, col, cor, did, sid, pid):
    dao = get_bib(col).sqldao
    corpus = dao.get_corpus(cor)
    doc = dao.doc.by_id(did)
    sent = dao.get_sent(sid, readingIDs=(pid,))
    c = get_context({'title': 'Sentence: ' + sent.text,
                     'col': col,
                     'corpus': corpus,
                     'doc': doc,
                     'sid': sid,
                     'sent_ident': sent.ident,
                     'pid': pid})
    # convert Visko Sentence into ISF to display
    # [TODO] Fix this
    c.update({'sent': sent, 'parse': sent[0].dmrs()})
    return render(request, "visko2/corpus/parse.html", c)


##########################################################################
# REST APIs
##########################################################################

@jsonp
def rest_fetch(request, col, cor, did, sid, pid=None):
    dao = get_bib(col).sqldao
    if pid:
        sent = dao.get_sent(sid, readingIDs=(pid,))
    else:
        sent = dao.get_sent(sid)
    j = sent2json(sent)
    return j


@csrf_protect
@jsonp
def rest_note_sentence(request, col, cor, did, sid):
    name = request.POST.get('name', '')  # should be sent_comment
    value = request.POST.get('value', '')  # value
    pk = request.POST.get('pk', '')  # sent_id
    dao = get_bib(col).sqldao
    sent = dao.get_sent(sid)
    if name != 'sent_comment' or not pk or int(pk) != sent.ID:
        getLogger().warning("Name = {} | Value = {} | pk = {}".format(name, value, pk))
        raise Exception("Invalid sentence information was provided")
    else:
        dao.note_sentence(sent.ID, value)
        return {}


@csrf_protect
@jsonp
def rest_doc_title(request, col, cor, did):
    print("Editing doc_title")
    name = request.POST.get('name', '')  # should be doc_title
    value = request.POST.get('value', '')  # value
    pk = request.POST.get('pk', '')  # doc_name
    dao = get_bib(col).sqldao
    doc = dao.doc.by_id(did)
    if name != 'doc_title' or not pk or pk != doc.name:
        getLogger().warning("Name = {} | Value = {} | pk = {}".format(name, value, pk))
        raise Exception("Invalid document information was provided")
    else:
        doc.title = value
        getLogger().info("Updating title of document #{} from {} to {}".format(doc.ID, pk, value))
        dao.save_doc(doc, 'title')
        return {}


@csrf_protect
@jsonp
def rest_flag_sentence(request, col, cor, did, sid):
    name = request.POST.get('name', '')  # should be sent_flag
    value = request.POST.get('value', '')  # value
    pk = request.POST.get('pk', '')  # sent_id
    dao = get_bib(col).sqldao
    sent = dao.get_sent(sid)
    if name != 'sent_flag' or not pk or int(pk) != sent.ID:
        getLogger().warning("Name = {} | Value = {} | pk = {}".format(name, value, pk))
        raise Exception("Invalid sentence information was provided")
    else:
        dao.flag_sent(sent.ID, value)
        return {}


@jsonp
def rest_data_flag_all(request):
    return SENT_FLAGS


@csrf_protect
@jsonp
def rest_dmrs_parse(request, col=None, cor=None, did=None, sid=None, pid=None):
    dmrs_raw = request.POST.get('dmrs', '')
    surface = request.POST.get('surface', '')
    transform = request.POST.get('transform', '')
    # create a new Sentence object or reuse the old one?
    if col and sid and pid:
        dao = get_bib(col).sqldao
        sent = dao.sentence.by_id(sid)
    else:
        sent = Sentence(text=surface)
    # to parse from raw text or from DMRS string?
    reading = None
    if not dmrs_raw and surface:
        # generate dmrs from surface
        result = ghub.ERG.parse(surface, parse_count=1)
        if len(result):
            reading = result[0]
        else:
            raise Exception("Cannot parse surface string")
    if reading is not None:
        # use reading object
        sent.readings.append(reading)
    else:
        sent.add(dmrs_str=dmrs_raw)
    if pid:
        sent[0].ID = pid
    sent.mode = Reading.ACTIVE
    if transform:
        t = Transformer()
        t.apply(sent)
    return sent2json(sent)


@csrf_protect
@jsonp
def rest_dmrs_save(request, action, col, cor, did, sid, pid):
    if action not in ('insert', 'replace'):
        raise Exception("Invalid action provided")
    dao = get_bib(col).sqldao
    sent = dao.get_sent(sid, readingIDs=(pid,))

    # Parse given DMRS
    dmrs_raw = request.POST.get('dmrs', '')

    if action == 'replace':
        # this will replace old (existing) DMRS
        dao.delete_reading(pid)
        # assign a new ident to this new parse
    sentinfo = dao.get_sent(sent.ID, skip_details=True)
    try:
        reading = sent.add(dmrs_str=dmrs_raw)
        reading.rid = '{}-manual'.format(len(sentinfo))
        reading.mode = Reading.ACTIVE
        reading.sentID = sent.ID
    except Exception as e:
        getLogger().exception("DMRS string is not well-formed")
        raise e
    dao.save_reading(reading)
    if reading.ID:
        # complete
        return {"success": True, "url": reverse('visko2:view_parse', args=[col, cor, did, sid, reading.ID])}
    else:
        raise Exception("Error occurred while creating reading")


@csrf_protect
@jsonp
def rest_dmrs_delete(request, col, cor, did, sid, pid):
    dao = get_bib(col).sqldao
    try:
        dao.delete_reading(pid)
        return {"success": True, "url": reverse('visko2:list_parse', args=[col, cor, did, sid])}
    except Exception as e:
        getLogger().exception("Cannot delete parse ID={}".format(pid))
        raise e
