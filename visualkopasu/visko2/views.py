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

from django.template import Context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.context_processors import csrf

from chirptext.texttaglib import TagInfo
from coolisf.util import Grammar

from visualkopasu.util import getLogger
from visualkopasu.kopasu import Biblioteche, Biblioteca
from visualkopasu.kopasu.util import getSentenceFromXML, getDMRSFromXML
from visualkopasu.kopasu.util import dmrs_str_to_xml, xml_to_str
from visualkopasu.kopasu.models import Document, ParseRaw, Interpretation

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
                 "collections": getAllCollections(),
                 "RESULTS": RESULTS, "input_results": 5})
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
        sent = Grammar().parse(sentence_text, parse_count=input_results)
        # tag sentences
        sent.tag(method=TagInfo.LELESK)
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
        isent = Grammar().parse(sentence_text, parse_count=input_results)
        isent.tag(method='lelesk')
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
    # if len(sent) == 1:
    #     # redirect to first parse to edit quicker
    #     return redirect('visko2:edit_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=sent_id, parse_id=sent[0].ID, mode='edit')
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
        c.update({'sent': sent.to_isf()})
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
    logger.info("Sent: {} | parse_id: {} | length: {}".format(sent, parse_id, len(sent)))
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
    print("vDMRS: {}".format(sent[0].dmrs[0]))
    for n in sent[0].dmrs[0].nodes:
        if str(n.nodeid) == '10007':
            print(n, n.rplemma, n.rplemmaID)
    c.update({'sent': isfsent, 'parse': isfsent[0], 'vdmrs': sent[0].dmrs[0]})
    c.update(csrf(request))
    return render(request, "visko2/corpus/parse.html", c)


def edit_parse(request, collection_name, corpus_name, doc_id, sent_id, parse_id, mode):
    dao = get_bib(collection_name).sqldao
    corpus = dao.getCorpus(corpus_name)[0]
    doc = dao.getDocument(doc_id)
    sent = dao.getSentence(sent_id, interpretationIDs=(parse_id,))
    if mode == 'delete' and str(sent[0].ID) == parse_id:
        try:
            logging.warning("Deleting interpretation: {}".format(parse_id))
            dao.deleteInterpretation(parse_id)
        except Exception as e:
            logger.error("Cannot delete parse ID={}. Error: {}".format(parse_id, e))
        return redirect('visko2:list_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=sent_id)

    # logger.info("Sent: {} | parse_id: {} | length: {}".format(sent, parse_id, len(sent)))
    c = Context({'title': 'Corpus',
                 'header': 'Visual Kopasu - 2.0',
                 'collection_name': collection_name,
                 'corpus': corpus,
                 'doc': doc,
                 'sent_id': sent_id})
    # update reparse count
    input_results = 5
    c.update({'input_results': input_results, 'RESULTS': RESULTS})
    # try to parse DMRS from raw
    #
    action = request.POST.get('btn_action', None)
    print("Action: ", action)
    dmrs_raw = request.POST.get('dmrs_raw', None)
    if dmrs_raw:
        # replace current parse
        # logger.info("DMRS raw: {}".format(dmrs_raw))
        dmrs_xml = dmrs_str_to_xml(dmrs_raw)
        # logger.info("DMRS xml: {}".format(etree.tostring(dmrs_xml)))
        dmrs = getDMRSFromXML(dmrs_xml)
        sent.mode = Interpretation.ACTIVE
        sent.interpretations[0].dmrs = [dmrs]
        sent.interpretations[0].raws = [ParseRaw(xml_to_str(dmrs_xml), rtype=ParseRaw.XML)]
        # if action = insert (i.e. save as new DMRS)
        if action in ('insert', 'save'):
            if action == 'save':
                # this will replace old (existing) DMRS
                dao.deleteInterpretation(parse_id)
            # assign a new ident to this new parse
            sentinfo = dao.getSentence(sent.ID, skip_details=True, get_raw=False)
            new_parse = Interpretation(rid='{}-manual'.format(len(sentinfo)), mode=Interpretation.ACTIVE)
            new_parse.sentenceID = sent.ID
            new_parse.dmrs.append(dmrs)
            new_parse.raws = [ParseRaw(xml_to_str(dmrs_xml), rtype=ParseRaw.XML)]
            dao.saveInterpretation(new_parse, doc.ID)
            if new_parse.ID:
                return redirect('visko2:edit_parse', collection_name=collection_name, corpus_name=corpus_name, doc_id=doc_id, sent_id=sent_id, parse_id=new_parse.ID, mode='edit')
            else:
                raise Exception("Error occurred while creating interpretation")
                pass
    # convert Visko Sentence into ISF to display
    #
    isfsent = sent.to_isf()
    print("Visko sent: {}".format(len(sent)))
    print("ISF sent: {}".format(len(isfsent)))
    # print("vdmrs: {}".format(sent[0].dmrs[0]))
    c.update({'sent': isfsent, 'parse': isfsent[0], 'vdmrs': sent[0].dmrs[0]})
    c.update(csrf(request))
    return render(request, "visko2/corpus/parse.html", c)
