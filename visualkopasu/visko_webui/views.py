'''
Django settings for VisualKopasu project.
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
import logging
from collections import namedtuple

import xml.etree.ElementTree as ET

from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import Http404
from django.template import Context
# from django.template import loader
from django.shortcuts import redirect
from django.shortcuts import render

from chirptext.leutile import Counter

from visualkopasu.kopasu.models import Sentence
from visualkopasu.kopasu.models import Interpretation
from visualkopasu.config import ViskoConfig as vkconfig
from visualkopasu.kopasu.dmrs_search import LiteSearchEngine
from visualkopasu.kopasu.util import getDMRSFromXML
from visualkopasu.kopasu.util import getDMRSFromXMLString
from .clientutil import DMRSNodeTooltip
from .clientutil import TooltipURL
from .clientutil import DataUtil

# ISF support
from coolisf.main import PredSense
from coolisf.util import Grammar
from coolisf.gold_extract import sentence_to_xml
from coolisf.gold_extract import prettify_xml

cvarsort_dict = { 'x' : 'individual', 'e' : 'event', 'i' : 'undefined', 'u' : 'unknown' }
num_dict = { 'sg' : 'singular', 'pl' : 'plural', 'u' : 'unknown'}

class DMRSItem:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

DMRSBasketItem=namedtuple('DMRSBasketItem', ['sentenceID', 'interpretationID'])

class DMRSBasket:
    def __init__(self, items=None):
        self.items = [] if items is None else items
    
    def add(self, sentenceID, interpretationID):
        sentenceID = str(sentenceID)
        interpretationID = str(interpretationID)
        if not sentenceID or not interpretationID:
            # logging.debug("Invalid sentenceID or interpretationID")
            return # bad sentenceID or interpretationID 
        for item in self.items:
            if item.sentenceID == sentenceID and item.interpretationID == interpretationID:
                return # item exists
        # Item doesn't exists
        self.items.append(DMRSBasketItem(sentenceID=sentenceID, interpretationID=interpretationID))
    
    def count(self):
        return len(self.items)
    
    def contains(self, sentenceID, interpretationID):
        sentenceID = str(sentenceID)
        interpretationID = str(interpretationID)
        for item in self.items:
            if item.sentenceID == sentenceID and item.interpretationID == interpretationID:
                return True
        return False
    
    def remove(self, sentenceID, interpretationID):
        sentenceID = str(sentenceID)
        interpretationID = str(interpretationID)
        if sentenceID == '' and interpretationID == '':
            self.items = []
        else:
            for item in self.items:
                if item.sentenceID == sentenceID and item.interpretationID == interpretationID:
                    self.items.remove(item)
    
    def save(self, request):
        if request:
            request.session['visual_kopasu_dmrs_basket'] = self.items
    
    @staticmethod
    def instance(request):
        if 'visual_kopasu_dmrs_basket' in request.session:
            basket = DMRSBasket(request.session['visual_kopasu_dmrs_basket'])
            return basket
        else:
            basket = DMRSBasket()
            request.session['visual_kopasu_dmrs_basket'] = basket.items
        return basket


def build_tooltip(a_node):
    # TODO: clean up this mess please
    tooltip = DMRSNodeTooltip(3,3)
    if a_node.sense:
        sense_text = "{synsetid}: {lemma}".format(synsetid=a_node.sense.synsetid, lemma=a_node.sense.lemma)
        sense_url = 'http://compling.hss.ntu.edu.sg/omw/cgi-bin/wn-gridx.cgi?synset=' + a_node.sense.synsetid
        tooltip.push(TooltipURL(sense_text, sense_url))
    if a_node.rplemma:
        tooltip.push("RP.lemma:%s" % a_node.rplemma)
        if a_node.rppos:
            tooltip.push("RP.POS:%s" % a_node.rppos)
        if a_node.rpsense:
            tooltip.push("RP.sense:%s" % a_node.rpsense)
    if a_node.sortinfo:
        if a_node.sortinfo.cvarsort:
            tooltip.push("cvarsort:%s" % DataUtil.translate(a_node.sortinfo.cvarsort, cvarsort_dict))
        if a_node.sortinfo.num:
            tooltip.push("number:%s" % DataUtil.translate(a_node.sortinfo.num, num_dict))           
        if a_node.sortinfo.pers:
            tooltip.push("pers:%s" % DataUtil.translate(a_node.sortinfo.pers))
        if a_node.sortinfo.gend:
            tooltip.push("gend:%s" % DataUtil.translate(a_node.sortinfo.gend))
        if a_node.sortinfo.sf:
            tooltip.push("sf:%s" % DataUtil.translate(a_node.sortinfo.sf))                  
        if a_node.sortinfo.tense:
            tooltip.push("tense:%s" % DataUtil.translate(a_node.sortinfo.tense))
        if a_node.sortinfo.mood:
            tooltip.push("mood:%s" % DataUtil.translate(a_node.sortinfo.mood))
        if a_node.sortinfo.prontype:
            tooltip.push("prontype:%s" % DataUtil.translate(a_node.sortinfo.prontype))
        if a_node.sortinfo.prog:
            tooltip.push("prog:%s" % DataUtil.translate(a_node.sortinfo.prog))
        if a_node.sortinfo.perf:
            tooltip.push("perf:%s" % DataUtil.translate(a_node.sortinfo.perf))
        if a_node.sortinfo.ind:
            tooltip.push("ind:%s" % DataUtil.translate(a_node.sortinfo.ind))
    return tooltip.str()

def node_to_javascript(a_node, number_of_links):
    # Determine node's text
    # 1st priority is lemma
    text_type = ""
    if a_node.rplemma:
        text = a_node.rplemma
        text_type = "realpred"
    elif a_node.carg:
        text = a_node.carg
        text_type = "carg"
    elif a_node.gpred:
        text = a_node.gpred
        text_type = "gpred"
        if text.endswith('_rel'):
            text = text[:-4]

    node_template = u"var node_{id} = {{ 'text' : '{text}', 'from' : {cfrom}, 'to' : {cto}, 'type' : '{text_type}', 'pos': '{pos}', 'link_count' : {links}, 'tooltip' : {tooltip} }};"
    node_js = node_template.format(
                id=a_node.ID
                , text=text
                , cfrom=a_node.cfrom
                , cto=a_node.cto
                , text_type=text_type
                , links=number_of_links
                , tooltip=build_tooltip(a_node)
                , pos=a_node.rppos if a_node.rplemma and a_node.rppos else '')
    return node_js

rargname_shortform = {
                    'ARG1' : '1'
                    ,'ARG2' : '2'
                    ,'ARG3' : '3'
                    ,'ARG4' : '4'
                    ,'ARG' : 'A'
                    ,'L-INDEX' : 'LI'
                    ,'R-INDEX' : 'RI'
                    ,'L-HNDL' : 'LH'
                    ,'R-HNDL' : 'RH'
                    ,'RSTR' : 'RSTR'
                    }

def shorten_rargname(rargname):
    if rargname in rargname_shortform:
        return rargname_shortform[rargname]
    else:
        return rargname

def link_to_javascript(a_link):
    link_template = u"var link_{id} = {{ 'from': node_{fromNodeID}, 'to': node_{toNodeID}, 'post' : '{post}', 'rargname' : '{rargname}' }}; "
    link_js = link_template.format(
                                id = a_link.ID
                                , fromNodeID = a_link.fromNode.ID
                                , toNodeID = a_link.toNode.ID
                                , post = a_link.post
                                , rargname = shorten_rargname(a_link.rargname)
                                )
    return link_js

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

# ------------------------------------------------------------------
# VIEWS
# ------------------------------------------------------------------

def home(request):
    logging.debug(request.POST.get('user_query', ''))
    
    # dao = vkconfig.getDAO()    
    c = Context({
         'title'  : 'Home Page'
        ,'header' : 'Visual Kopasu'
        ,'biblioteche' : getAllCollections()
    })
    c.update(csrf(request))
    return render(request, "home/index.html", c)


def doc_display(request, collection_name, corpus_name, doc_id):
    doc_id = int(doc_id)
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    document = dao.getDocument(doc_id)
    sentences = dao.getSentences(doc_id)
    
    c = Context({'title' : 'Document viewer'
    ,'header': 'Document'
    ,'collection_name' : collection_name
    ,'corpus_name' : corpus_name
    ,'document' : document
    ,'sentences' : sentences
    })
    c.update(csrf(request))
    return render(request, "doc_display/index.html", c)

def dmrs_display(request, collection_name, corpus_name, doc_id, sentence_id, interpretation_id=None):
    search_count = None
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    
    if not interpretation_id:
        sentence = dao.getSentence(sentence_id, mode='active')
    else:
        sentence = dao.getSentence(sentence_id, interpretationIDs=[interpretation_id])

    if (not sentence) or len(sentence.interpretations) == 0:
        raise Http404
    
    js_sentence = sentence_to_javascript(sentence, dao)     
    sentence_interpretations = dao.getSentence(sentence_id, skip_details=True).interpretations
    
    c = Context({'title' : sentence.text
    ,'header': 'DMRS'
    ,'collection_name' : collection_name
    ,'corpus_name' : corpus_name
    ,'sentence_info' : js_sentence
    ,'interpretations' : sentence_interpretations
    ,'added_to_basket' : DMRSBasket.instance(request).contains(sentence.ID, js_sentence.interpretation.ID)
    ,'basket_size' : DMRSBasket.instance(request).count()
    })
    return render(request, "dmrs_display/index.html", c)

def original_display(request, collection_name, corpus_name, doc_name, sentence_ident, interpretationID=''):
    dao = vkconfig.BibliotecheMap[collection_name].textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc_name)
    content = dao.getDMRSRaw(sentence_ident, interpretationID)
    
    title = 'Original XML of %s:%s' % (sentence_ident, interpretationID) if interpretationID else 'Original XML of %s' % (sentence_ident,)
    c = Context({
         'title'  : title
        ,'header' : title
        ,'collection_name' : collection_name
        ,'corpus_name' : corpus_name
        ,'content' : content if content is not None and len(content) > 0 else ''
        ,'doc_name' : doc_name
        ,'sentence_ident' : sentence_ident
        ,'interpretationID' : interpretationID
    })
    c.update(csrf(request))
    return render(request, "dmrs_display/xml.html", c)

def search(request):
    DEFAULT_LIMIT = 10000 # result limit
    engines = []
    collection = request.POST.get('collection_name', '')
    logging.debug("collection = %s" % (collection,))
    if collection:
        logging.debug("Limited search in collection %s" % (collection,))
        dao = vkconfig.BibliotecheMap[collection].sqldao
        engine = LiteSearchEngine(dao, limit=DEFAULT_LIMIT)
        engines.append(engine)
    else:
        for bib in vkconfig.Biblioteche:
            engine = LiteSearchEngine(bib.sqldao, limit=DEFAULT_LIMIT)
            engines.append(engine)
    try:
        user_query = request.POST.get('user_query', '')
        logging.debug("User query: %s" % user_query)
        search_statistics = ''
        search_results = None
        dmrs_search_results = None
        sentences = []
        for engine in engines:
            res = engine.search(user_query)
            if res:
                sentences += res

        if sentences:
            search_results = sentences
            logging.info("Query: [%s] - Found: %s sentence(s)" % (user_query, len(search_results)))
            # Store search result to session
            dmrs_search_results = [] 
            for sentence in sentences:
                for interpretation in sentence.interpretations:
                    interpretation.set_property("search_ID", len(dmrs_search_results))
                    dmrs_search_results.append({ "sentence" : sentence.ID, "interpretation" : interpretation.ID })
            request.session['dmrs_search_results'] = dmrs_search_results
            # Build statistics
            search_statistics = ('%d sentences' if len(search_results) > 1 else '%d sentence') % len(search_results)
            search_statistics += (' - %d interpretations' if len(search_results) > 1 else '%d interpretation') % len(dmrs_search_results)
            if len(dmrs_search_results) == DEFAULT_LIMIT:
                search_statistics += " [MAX]"
    except Exception as e:
        logging.exception("Search exception: %s" % e)
        dmrs_search_results = None
        search_results = None
        pass
    
    #logging.debug("Search results: %s" % search_results)
    
    c = Context({
         'title'  : 'Search Results' if user_query else 'Search'
        ,'header' : 'Search Results' if user_query else 'Search'
        ,'search_results' : search_results
        ,'dmrs_search_results' : dmrs_search_results
        ,'user_query' : user_query
        ,'search_statistics' : search_statistics
        , 'collection_name' : collection
    })
    c.update(csrf(request))
    return render(request, "search/index.html", c)

def dmrs_search_display(request, collection_name, search_id):
    search_id = int(search_id)
    search_count = None    
    dao = vkconfig.BibliotecheMap[collection_name].sqldao
    
    prev_search = False
    next_search = False
    if search_id >= 0:
        search_item = request.session['dmrs_search_results'][search_id]
        sentence_id = search_item['sentence']
        interpretation_id = search_item['interpretation']
        sentence = dao.getSentence(sentence_id, interpretationIDs=[interpretation_id])
        if(search_id > 0):
            prev_search = str(search_id - 1)
        else:
            prev_search = False
        
        search_count = len(request.session['dmrs_search_results'])
        if search_id < search_count - 1:
            next_search = str(search_id + 1)
        else:
            next_search = False
    else:
        raise Http404
    js_sentence = sentence_to_javascript(sentence, dao)
    sentence_interpretations = dao.getSentence(sentence_id, skip_details=True).interpretations
    c = Context({'title': sentence.text,
                 'header': 'DMRS',
                 'collection_name': collection_name,
                 'sentence_info': js_sentence,
                 'interpretations': sentence_interpretations,
                 'prev_search': prev_search,
                 'next_search': next_search,
                 'search_id': search_id+1,
                 'search_count': search_count,
                 'added_to_basket': DMRSBasket.instance(request).contains(sentence.ID, js_sentence.interpretation.ID),
                 'basket_size': DMRSBasket.instance(request).count()
                 })
    return render(request, "dmrs_display/index.html", c)


def sentence_to_javascript(sentence, dao=None):
    '''
    Convert the first DMRS of the first interpretation to javascript
    '''
    document = dao.getDocument(sentence.documentID) if dao else ''
    corpus = dao.getCorpusByID(document.corpusID) if dao else ''
    if sentence and len(sentence.interpretations) > 0:
        i = sentence.interpretations[0]
        return dmrs_to_js(sentence.text, i.dmrs[0], corpus, document, sentence, i)


def dmrs_to_js(sentence_text, dmrs, corpus=None, document=None, sentence=None, interpretation=None):
    node_list = ''
    node_id_list = []
    link_list = ''
    link_id_list = []
    sentence_text = sentence_text.replace('\'', '\\\'').replace('\r', '').replace('\n', '')

    link_counter = Counter()
    for a_link in dmrs.links:
        if not a_link.ID:
            a_link.ID = len(link_id_list) + 1
        if not a_link.fromNode.ID:
            a_link.fromNode.ID = a_link.fromNode.nodeid
        if not a_link.toNode.ID:
            a_link.toNode.ID = a_link.toNode.nodeid
        link_list += link_to_javascript(a_link) + "\n\t\t\t\t"
        link_id_list.append("link_" + str(a_link.ID))
        link_counter.count(a_link.fromNode.ID)
        link_counter.count(a_link.toNode.ID)

    for a_node in dmrs.nodes:
        if a_node.ID == -1:
            a_node.ID = a_node.ident
            logging.debug('ID: %s' % (a_node.ID))
        node_list += node_to_javascript(a_node, link_counter[a_node.ID]) + "\n\t\t\t\t"
        node_id_list.append("node_" + str(a_node.ID))
    logging.debug(node_list)

    return DMRSItem(sentence_text=sentence_text,
                    node_list=node_list,
                    node_id_list=', '.join(node_id_list),
                    link_list=link_list,
                    link_id_list=', '.join(link_id_list),
                    corpus=corpus,
                    document=document,
                    sentence=sentence,
                    interpretation=interpretation,
                    dmrs_str='',
                    mrs_str='',
                    dmrs_json='',
                    mrs_json=''
                    )


def basket(request):
    try:
        command = request.GET.get('action', 'view')
        sentenceID = request.GET.get('id', '')
        interpretationID = request.GET.get('r', '')
    except:
        command = 'view'
    dao = vkconfig.getDAO()
    if command == 'remove':
        logging.debug("Removing from basket: sentenceID=%s (interpretationID=%s)" % (sentenceID, interpretationID))
        DMRSBasket.instance(request).remove(sentenceID, interpretationID)
        DMRSBasket.instance(request).save(request)
        # redirect to view
        return redirect("/basket")
    if command == 'add':
        logging.debug("Adding sentenceID=%s (interpretationID=%s)" % (sentenceID, interpretationID))
        DMRSBasket.instance(request).add(sentenceID, interpretationID)
        DMRSBasket.instance(request).save(request)
        # redirect to view
        return redirect("/basket")
    if command == 'view':
        # display basket
        basket = DMRSBasket.instance(request)
        dmrses = []
        logging.debug("Basket size: %s" % len(basket.items))
        for item in basket.items:
            logging.debug("Adding sentenceID=%s (interpretationID=%s)" % (item.sentenceID, item.interpretationID))
            sentence = dao.getSentence(item.sentenceID, interpretationIDs=[item.interpretationID])
            dmrs = sentence_to_javascript(sentence, dao)
            if dmrs:
                dmrses.append(dmrs)
        # Now display all sentences
                    
    c = Context({'title' : 'DMRS Basket'
                ,'header': 'DMRS Basket'
                ,'dmrses' : dmrses
    })
    return render(request, "basket/index.html", c)  

def isf_parse(request):
    sentence_text = request.POST.get('sentence', None)
    parse_result = Grammar().txt2dmrs(sentence_text)
    # with sense tags
    sentence_xml_node = sentence_to_xml(parse_result)

    sentence = Sentence(text=sentence_text)
    js_dmrses = []
    # for debug
    dmrs_xml_strings = []

    for mrs, mrs_node in zip(parse_result.mrs, sentence_xml_node.findall('./dmrses/dmrs')):
        # for debug
        xmlstr = ET.tostring(mrs_node, encoding='utf-8').decode('utf-8')
        dmrs_xml_strings.append(xmlstr)
        # build visualkopasu.kopasu.models.DMRS object
        DMRS_obj = getDMRSFromXML(mrs_node)
        dmrs_js = dmrs_to_js(sentence_text, DMRS_obj)
        dmrs_js.dmrs_str = mrs.dmrs_str()
        dmrs_js.mrs_str = mrs.mrs_str()
        dmrs_js.dmrs_json = mrs.dmrs_json()
        dmrs_js.mrs_json = mrs.mrs_json()
        js_dmrses.append(dmrs_js)

    c = Context({'title': sentence.text,
                 'header': 'Integrated Semantic Framework',
                 'dmrses': js_dmrses,
                 'sentence_text': sentence.text})
    c.update(csrf(request))
    return render(request, "coolisf/index.html", c)


def dev_test(request):
    # What do we need to display a sentence?
    sentence_id = 1010
    dao = vkconfig.BibliotecheMap['redwoods'].textdao.getCorpusDAO('redwoods').getDocumentDAO('cb')
    sentence = dao.getSentence(sentence_id)

    js_sentence = sentence_to_javascript(sentence)
    # sentence_interpretations = sentence.interpretations

    text = 'Dogs are funnier than Asian tiger mosquitoes.'
    results = Grammar().txt2dmrs(text)
    mrs_json = results.mrs[0].mrs_json()
    dmrs_json = results.mrs[0].dmrs_json()
    mrs = results.mrs[0].mrs_str()
    dmrs = results.mrs[0].dmrs_str()

    sentence_xml_node = sentence_to_xml(results)
    first_dmrs_xml = sentence_xml_node.findall('./dmrses/dmrs')[0]
    dmrs_isf = dmrs_to_js(text, getDMRSFromXML(first_dmrs_xml))
    c = Context({'title': sentence.text,
                'header': 'DMRS',
                 'sentence_info': js_sentence,
                 'text': text,
                 'mrs': mrs,
                 'dmrs': dmrs,
                 'mrs_json': mrs_json,
                 'dmrs_json': dmrs_json,
                 'dmrs_isf': dmrs_isf})
    return render(request, "dev_test/index.html", c)


def dev_viz(request):
    '''Delphin-viz demo'''
    c = Context({'title': 'Delphin-viz demo',
                 'header': 'Delphin-viz demo',
                 'sentence_info': ''})
    return render(request, "dev_test/viz.html", c)


def isf_parse_raw(request):
    ''' Parse a sentence using ISF and then display its DMRS
    '''
    sentence = request.POST.get('sentence', None)
    results = Grammar().txt2dmrs(sentence)
    mrses = None
    if results and results.mrs:
        logging.debug(results.mrs[0].preds())
        mrses = [PredSense.tag_sentence(mrs).replace('\n', '<br/>\n') for mrs in results.mrs]
    c = Context({'sentence': sentence,
                 'mrses': mrses})
    logging.debug(results.mrs)
    c.update(csrf(request))
    return render(request, 'coolisf/raw.html', c)
