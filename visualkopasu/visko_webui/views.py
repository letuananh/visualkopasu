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

import logging
from collections import namedtuple

from django.core.context_processors import csrf
from django.http import HttpResponse
from django.template import Context
# from django.template import loader
from django.shortcuts import redirect
from django.shortcuts import render

from visualkopasu.config import VisualKopasuConfiguration as vkconfig

from visualkopasu.kopasu.dao import DocumentDAO 
from visualkopasu.kopasu.dmrs_search import LiteSearchEngine
from .clientutil import DMRSNodeTooltip, DataUtil

#def display(request, a_template, a_context):
#    t = loader.get_template(a_template)
#    return HttpResponse(t.render(a_context))

cvarsort_dict = { 'x' : 'individual', 'e' : 'event', 'i' : 'undefined', 'u' : 'unknown' }
num_dict = { 'sg' : 'singular', 'pl' : 'plural', 'u' : 'unknown'}

def build_tooltip(a_node):
    tooltip = DMRSNodeTooltip(3,3)
    if a_node.realpred:
        if DataUtil.notEmpty(a_node.realpred.pos):
            tooltip.push("pos:%s" % a_node.realpred.pos)
        if DataUtil.notEmpty(a_node.realpred.sense):
            tooltip.push("RP.sense:%s" % a_node.realpred.sense)
    if a_node.sortinfo:
        if DataUtil.notEmpty(a_node.sortinfo.cvarsort):
            tooltip.push("cvarsort:%s" % DataUtil.translate(a_node.sortinfo.cvarsort, cvarsort_dict))
        if DataUtil.notEmpty(a_node.sortinfo.num):
            tooltip.push("number:%s" % DataUtil.translate(a_node.sortinfo.num, num_dict))           
        if DataUtil.notEmpty(a_node.sortinfo.pers):
            tooltip.push("pers:%s" % DataUtil.translate(a_node.sortinfo.pers))
        if DataUtil.notEmpty(a_node.sortinfo.gend):
            tooltip.push("gend:%s" % DataUtil.translate(a_node.sortinfo.gend))
        if DataUtil.notEmpty(a_node.sortinfo.sf):
            tooltip.push("sf:%s" % DataUtil.translate(a_node.sortinfo.sf))                  
        if DataUtil.notEmpty(a_node.sortinfo.tense):
            tooltip.push("tense:%s" % DataUtil.translate(a_node.sortinfo.tense))
        if DataUtil.notEmpty(a_node.sortinfo.mood):
            tooltip.push("mood:%s" % DataUtil.translate(a_node.sortinfo.mood))
        if DataUtil.notEmpty(a_node.sortinfo.prontype):
            tooltip.push("prontype:%s" % DataUtil.translate(a_node.sortinfo.prontype))
        if DataUtil.notEmpty(a_node.sortinfo.prog):
            tooltip.push("prog:%s" % DataUtil.translate(a_node.sortinfo.prog))
        if DataUtil.notEmpty(a_node.sortinfo.perf):
            tooltip.push("perf:%s" % DataUtil.translate(a_node.sortinfo.perf))
        if DataUtil.notEmpty(a_node.sortinfo.ind):
            tooltip.push("ind:%s" % DataUtil.translate(a_node.sortinfo.ind))
    return tooltip.str()

def node_to_javascript(a_node, number_of_links):
    # Determine node's text
    # 1st priority is lemma
    text_type = ""
    if a_node.realpred:
        text = a_node.realpred.lemma
        text_type = "realpred"
    elif a_node.carg:
        text = a_node.carg
        text_type = "carg"
    elif a_node.gpred:
        text = a_node.gpred.value
        text_type = "gpred"
        if text.endswith('_rel'):
            text = text[:-4]
        
    # text = a_node.realpred.lemma if a_node.realpred 
    # else (a_node.carg if a_node.carg 
    # else a_node.gpred.value)
    
    node_template = u"var node_{id} = {{ 'text' : '{text}', 'from' : {cfrom}, 'to' : {cto}, 'type' : '{text_type}', 'pos': '{pos}', 'link_count' : {links}, 'tooltip' : {tooltip} }};"
    node_js = node_template.format(
                id=a_node.ID
                , text=text
                , cfrom=a_node.cfrom
                , cto=a_node.cto
                , text_type=text_type
                , links=number_of_links
                , tooltip=build_tooltip(a_node)
                , pos=a_node.realpred.pos if a_node.realpred and a_node.realpred.pos else '')
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
                                , post = a_link.post.value
                                , rargname = shorten_rargname(a_link.rargname.value)
                                )
    return link_js

class Counter:
    def __init__(self):
        self.counter = {}
        
    def count(self, key):
        if not key in self.counter:
            self.counter[key] = 1
        else:
            self.counter[key] += 1
            
    def number(self, key):
        if not key in self.counter:
            return 0
        else:
            return self.counter[key]

def doc_display(request, doc_id):
    database = request.GET.get('db', None)
    doc_id = int(doc_id)
    dao = vkconfig.getDAO(database)
    document = dao.getDocument(doc_id)
    sentences = dao.getSentences(doc_id)
    
    c = Context({'title' : 'Document viewer'
    ,'header': 'Document'
    ,'document' : document
    ,'sentences' : sentences
    })
    c.update(csrf(request))
    return render(request, "doc_display/index.html", c)

def home(request):
    print(request.POST.get('user_query', ''))
    
    # dao = vkconfig.getDAO()
    corpora = []
    for dao in vkconfig.SQLDAOs:
        corpora += dao.getCorpora()

        for corpus in corpora:
            corpus.set_property("dbname", dao.config['dbname'])
            print("Found a corpus: %s at db %s" % (corpus.name, corpus.dbname))
            corpus.documents = dao.getDocumentOfCorpus(corpus.ID)
            for doc in corpus.documents:
                print(" -> Doc: %s" % doc.name)
    
    c = Context({
         'title'  : 'Home Page'
        ,'header' : 'Visualisation module'
        ,'corpora' : corpora
    })
    c.update(csrf(request))
    return render(request, "home/index.html", c)

def search(request):
    DEFAULT_LIMIT = 10000 # result limit
    dao = vkconfig.getDAO()
    engine = LiteSearchEngine(dao, limit=DEFAULT_LIMIT)
    try:
        user_query = request.POST.get('user_query', '')
        print("User query: %s" % user_query)
        search_statistics = ''
        search_results = None
        dmrs_search_results = None
        sentences = engine.search(user_query)
        
        if sentences != None:
            search_results = sentences
            logging.info("Query: [%s] - Found: %s sentence(s)" % (user_query, len(search_results)))
            # Store search result to session
            dmrs_search_results = [] 
            for sentence in sentences:
                for representation in sentence.representations:
                    representation.set_property("search_ID", len(dmrs_search_results))
                    dmrs_search_results.append({ "sentence" : sentence.ID, "representation" : representation.ID })
            request.session['dmrs_search_results'] = dmrs_search_results
            # Build statistics
            search_statistics = ('%d sentences' if len(search_results) > 1 else '%d sentence') % len(search_results)
            search_statistics += (' - %d representations' if len(search_results) > 1 else '%d representation') % len(dmrs_search_results)
            if len(dmrs_search_results) == DEFAULT_LIMIT:
                search_statistics += " [MAX]"
    except Exception as e:
        logging.exception("Search exception: %s" % e)
        dmrs_search_results = None
        search_results = None
        pass
    
    #print("Search results: %s" % search_results)
    
    c = Context({
         'title'  : 'Search Results' if user_query else 'Search'
        ,'header' : 'Search Results' if user_query else 'Search'
        ,'search_results' : search_results
        ,'dmrs_search_results' : dmrs_search_results
        ,'user_query' : user_query
        ,'search_statistics' : search_statistics
    })
    c.update(csrf(request))
    return render(request, "search/index.html", c)

def dmrs_display(request, sentence_id):
    search_count = None
    try:
        database = request.GET.get('db', None)
        sentence_id = int(sentence_id)
        representation_id = request.GET.get('r', '')
        search_id = int(request.GET.get('search_id', '-1'))
    except:
        return redirect("/dmrs/1")
        sentence_id = 1
    
    dao = vkconfig.getDAO(database)
    
    # print('Fetching id=%s repre=%s' %(sentence_id, representation_id))
    
    prev_search = False
    next_search = False
    if search_id >= 0:
        search_item = request.session['dmrs_search_results'][search_id]
        sentence_id = search_item['sentence'] 
        representation_id = search_item['representation']
        sentence = dao.getSentence(sentence_id, representationIDs=[representation_id])
        if(search_id > 0):
            prev_search = str(search_id - 1)
        else:
            prev_search = False
        
        search_count = len(request.session['dmrs_search_results'])
        if search_id < search_count - 1:
            next_search = str(search_id + 1)
        else:
            next_search = False
    elif not representation_id:
        sentence = dao.getSentence(sentence_id,mode='active')
    else:
        sentence = dao.getSentence(sentence_id, representationIDs=[representation_id])

    if (not sentence) or len(sentence.representations) == 0:
        return redirect("/dmrs/?id=1")
    
    js_sentence = sentence_to_javascript(sentence, dao)     
    sentence_representations = dao.getSentence(sentence_id, skip_details=True).representations
    
    c = Context({'title' : sentence.text
    ,'header': 'DMRS'
    ,'sentence_info' : js_sentence
    ,'representations' : sentence_representations
    ,'prev_search' : prev_search
    ,'next_search' : next_search
    ,'search_id' : search_id+1
    ,'search_count' : search_count
    ,'added_to_basket' : DMRSBasket.instance(request).contains(sentence.ID, js_sentence.representation.ID)
    ,'basket_size' : DMRSBasket.instance(request).count()
    })
    return render(request, "dmrs_display/index.html", c)

class DMRSItem:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

DMRSBasketItem=namedtuple('DMRSBasketItem', ['sentenceID', 'representationID'])

class DMRSBasket:
    def __init__(self, items=None):
        self.items = [] if items is None else items
    
    def add(self, sentenceID, representationID):
        sentenceID = str(sentenceID)
        representationID = str(representationID)
        if not sentenceID or not representationID:
            # print("Invalid sentenceID or representationID")
            return # bad sentenceID or representationID 
        for item in self.items:
            if item.sentenceID == sentenceID and item.representationID == representationID:
                # print("Item exists!")
                return # item exists
        # Item doesn't exists
        self.items.append(DMRSBasketItem(sentenceID=sentenceID, representationID=representationID))
        # print("Added, size = %s" % len(self.items))
    
    def count(self):
        return len(self.items)
    
    def contains(self, sentenceID, representationID):
        sentenceID = str(sentenceID)
        representationID = str(representationID)
        for item in self.items:
            # print("Comparing: %s v.s %s --- %s v.s %s" %(item.sentenceID, sentenceID, item.representationID, representationID))
            if item.sentenceID == sentenceID and item.representationID == representationID:
                return True
        return False
    
    def remove(self, sentenceID, representationID):
        sentenceID = str(sentenceID)
        representationID = str(representationID)
        if sentenceID == '' and representationID == '':
            self.items = []
        else:
            for item in self.items:
                if item.sentenceID == sentenceID and item.representationID == representationID:
                    self.items.remove(item)
    
    def save(self, request):
        if request:
            request.session['visual_kopasu_dmrs_basket'] = self.items
    
    @staticmethod
    def instance(request):
        if 'visual_kopasu_dmrs_basket' in request.session:
            #print("Retrieving basket from session")
            basket = DMRSBasket(request.session['visual_kopasu_dmrs_basket'])
            #print("Basket size = %s" % len(basket.items))
            return basket
        else:
            print("Basket doesn't exist, create a new one")
            basket = DMRSBasket()
            request.session['visual_kopasu_dmrs_basket'] = basket.items
        return basket

'''
Convert the first DMRS of the first representation to javascript
'''
def sentence_to_javascript(sentence, dao):
    if sentence and len(sentence.representations) > 0:
        # retrieved sentence, now convert DMRS to javascript code
        dmrs = sentence.representations[0].dmrs[0]
        node_list = ''
        node_id_list = []
        link_list = ''
        link_id_list = []       
        
        link_counter = Counter()
        for a_link in dmrs.links:
            link_list += link_to_javascript(a_link) + "\n\t\t\t\t"
            link_id_list.append( "link_" + str(a_link.ID) )
            link_counter.count(a_link.fromNode.ID)
            link_counter.count(a_link.toNode.ID)
            
        for a_node in dmrs.nodes:
            node_list += node_to_javascript(a_node, link_counter.number(a_node.ID)) + "\n\t\t\t\t"
            node_id_list.append( "node_" + str(a_node.ID) )
            
            
        #print "ident = %s" % sentence.representations[0].ident
        return DMRSItem(sentence_text=sentence.text.replace('\'', '\\\'').replace('\r','').replace('\n', '')
                        ,node_list=node_list
                        ,node_id_list=', '.join(node_id_list)
                        ,link_list=link_list
                        ,link_id_list=', '.join(link_id_list)
                        ,sentence=sentence
                        ,representation=sentence.representations[0]
                        ,document=dao.getDocument(sentence.documentID)
                        )
    else:
        return None

def basket(request):
    try:
        command = request.GET.get('action', 'view')
        sentenceID = request.GET.get('id', '')
        representationID = request.GET.get('r', '')
    except:
        command = 'view'
    
    dao = vkconfig.getDAO()
    
    if command == 'remove':
        print("Removing from basket: sentenceID=%s (representationID=%s)" % (sentenceID, representationID))
        DMRSBasket.instance(request).remove(sentenceID, representationID)
        DMRSBasket.instance(request).save(request)
        # redirect to view
        return redirect("/basket")      
    if command == 'add':
        print("Adding sentenceID=%s (representationID=%s)" % (sentenceID, representationID))
        DMRSBasket.instance(request).add(sentenceID, representationID)
        DMRSBasket.instance(request).save(request)
        # redirect to view
        return redirect("/basket")
    if command == 'view':
        # display basket
        basket = DMRSBasket.instance(request)
        dmrses = []
        print("Basket size: %s" % len(basket.items))
        for item in basket.items:
            print("Adding sentenceID=%s (representationID=%s)" % (item.sentenceID, item.representationID))
            sentence = dao.getSentence(item.sentenceID, representationIDs=[item.representationID])
            dmrs = sentence_to_javascript(sentence, dao)
            if dmrs:
                dmrses.append(dmrs)
        # Now display all sentences
                    
    c = Context({'title' : 'DMRS Basket'
                ,'header': 'DMRS Basket'
                ,'dmrses' : dmrses
    })
    return render(request, "basket/index.html", c)  

def original_display(request, document, sentenceID, representationID=''):
    dao = vkconfig.getDAO()
    
    try:
        database = request.GET.get('db', None)
        #document = request.GET.get('doc', '')
        #sentenceID = request.GET.get('id', '')
        #representationID = request.GET.get('r', '')
        #dao = getTextDAO(document)
        dao = vkconfig.getTextDAO(database)
        content = dao.getDMRSRaw(sentenceID, representationID, documentID=str(document))
        # content = '--'
    except Exception as e:
        print("Error: {e}".format(e=e))
        content = []
        raise e
    
    title = 'Original XML of %s:%s' % (sentenceID, representationID) if representationID else 'Original XML of %s' % (sentenceID,)
    c = Context({
         'title'  : title
        ,'header' : title
        ,'content' : content if content is not None and len(content) > 0 else ''
        ,'docID' : document
        ,'sentenceID' : sentenceID
    })
    c.update(csrf(request))
    return render(request, "dmrs_display/xml.html", c)
