'''
Data models for VisualKopasu project.
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
from .textutil import EncodingUtil
    
class BaseConcept:
    def __init__(self):
        pass
    
    def set_property(self, property, value):
        self.__dict__[property] = value
        return self
        
    def update_from(self, a_dict):
        for key in self.__dict__.keys():
            if key in a_dict:
                self.set_property(key, a_dict[key])
        return self
    
    def update_fields(self, map_info, a_dict):
        for pair in map_info:
            if type(pair) == list:
                # print("using list mode for %s" % pair)
                self.update_field(pair[1], pair[0], a_dict)
            elif type(pair) == str:
                self.update_field(pair, pair, a_dict)
            else:
                # TODO: error?
                pass
        return self
    
    def update_field(self, property_name, tag_attribute, a_dict):
        if not tag_attribute:
            tag_attribute = property_name
        if tag_attribute in a_dict:
            self.set_property(property_name, a_dict[tag_attribute])
        return self
            
    def __str__(self):
        return str(',\t '.join('%s : %s' % (k, str(v)) for (k, v) in self.__dict__.iteritems() if v))

'''
    A corpus wrapper
'''
class Corpus(BaseConcept):
    def __init__(self, name = ''):
        self.ID = None
        self.name = name
        self.documents = []
        pass
    
class Document(BaseConcept):
    def __init__(self, name = '', corpusID = None):
        self.ID = None
        self.name = name
        self.corpusID = corpusID
        self.corpus = None
        pass    

class Sentence(BaseConcept):
    def __init__(self, ident = 0, text = '', documentID = None):
        self.ID = None
        self.ident =  ident
        self.text = text
        self.documentID = documentID
        self.interpretations = []
        # self.dmrs = []
        # self.parseTrees = []

    def getInactiveInterpretation(self):
        return [repr for repr in self.interpretations if repr.mode == "inactive"]
    def getActiveInterpretation(self):
        return [repr for repr in self.interpretations if repr.mode == "active"]

    def __str__(self):
        return "[ID=" + self.ident + "]" + self.text
        #return u"[ID=%s] %s" % (self.ident, self.text)

class Interpretation(BaseConcept):   
    
    INACTIVE = 0
    ACTIVE = 1 
    
    def __init__(self, rid='', mode='', ID=None, dmrs=None, trees=None):
        self.ID = ID
        self.rid = rid
        self.mode = mode
        self.dmrs = dmrs if dmrs else list()
        self.parse_trees = trees if trees else list()
        self.sentenceID = None
        
    def __str__(self):
        return u"Interpretation [ID={rid}, mode={mode}]".format(rid=self.rid, mode=self.mode)

"""
Parse tree (synthetic tree)
"""
class ParseTree:
    def __init__(self, root, value = ''):
        self.value = value
        self.root = root

"""
A node of parse tree
"""
class ParseNode:
    def __init__(self, nodetype, value):
        self.nodetype = nodetype
        self.value = value
        self.children = []
        
    def __str__(self):
        return u"{type}: {value}".format(type=self.nodetype, value=self.value)

class DMRS(BaseConcept):
    """
    DMRS object default constructor
    """
    def __init__(self, ident = '', cfrom = -1, cto = -1, surface = ''):
        self.ID = None
        self.ident = ident
        self.cfrom = cfrom
        self.cto = cto
        self.surface = surface
        self.interpretationID = None
        
        # Nodes and links might be indexed for faster access
        self.nodes = []
        self.links = []
    
    def getNodeById(self, nodeid, use_record_ID = False):
        if use_record_ID:
            return [node for node in self.nodes if node.ID == nodeid]
        else:
            return [node for node in self.nodes if node.nodeid == nodeid]
    
    def getLink(self, fromid=None, toid=None):
        return [link for link in self.links if 
            ((not fromid) or link.fromNode.nodeid == fromid)
            and ((not toid) or link.toNode.nodeid == toid)]
        
    def __str__(self):
        nodes = ''
        for node in self.nodes:
            nodes += str(node) + "\n"
            
        links = ''
        for link in self.links:
            links += str(link) + "\n"
        return "DMRS: ident='{ident}', [{cfrom} : {to}], surface='{surface}'\n\n.:[Nodes]:.\n{nodes}\n.:[Links]:.\n{links}".format(ident=self.ident, cfrom=self.cfrom, to=self.cto, surface=self.surface, nodes=nodes, links=links)

class Node(BaseConcept):
    """
    Node object constructor
    """
    def __init__(self, nodeid = None, cfrom = -1, cto = -1, surface = '', base = '', carg = ''):
        self.ID = None
        self.nodeid = nodeid
        self.cfrom = cfrom
        self.cto = cto
        self.surface = surface 
        self.base = base
        self.carg = carg
        self.dmrsID = -1
        
        self.sortinfo = None
        self.gpred = None
        self.realpred = None 
        
    def __str__(self):
        return u"DMRS-Node: [ id={nodeid} [{cfrom}:{cto}] SORT_INFO={{{sortinfo}}} PRED={{{pred}}} ]".format(nodeid=self.nodeid, cfrom=self.cfrom, cto=self.cto, sortinfo=self.sortinfo, pred=str(self.gpred) if self.gpred != None else str(self.realpred))

class NodeIndex(BaseConcept):
    def __init__(self):
        self.nodeID = None
        self.carg = None
        
        self.lemmaID = None
        self.pos = None
        self.sense = None
        self.gpred_valueID = None
        self.dmrsID = None
        self.documentID = None

class LinkIndex(BaseConcept):
    def __init__(self):
        self.linkID = None
        self.fromNodeID = None
        self.toNodeID = None
        self.post = None
        self.rargname = None
        self.dmrsID = None
        self.documentID = None
"""
sortinfo of a Node
"""
class SortInfo(BaseConcept):
    
    def __init__(self, cvarsort = '', num = '', pers ='', gend = '', sf = '', tense = '', mood = '', prontype ='', prog ='', perf='', ind=''):
        self.ID = None
        self.cvarsort = cvarsort
        self.num = num
        self.pers = pers
        self.gend = gend
        self.sf = sf
        self.tense = tense
        self.mood = mood
        self.prontype = prontype
        self.prog = prog
        self.perf = perf
        self.ind = ind
        self.dmrs_nodeID = -1

    def __str__(self):
        return str(',\t '.join('%s : %s' % (k, str(v)) for (k, v) in self.__dict__.iteritems() if v))
"""
Gpred of a node
"""

"""
Grammar predicate
"""
class Gpred(BaseConcept):
    def __init__(self, value = None):
        self.ID = None
        self.value = value
        self.dmrs_nodeID = -1

"""
Lemma of Real pred
"""
class Lemma(BaseConcept):
    def __init__(self, lemma = None):
        self.ID = None
        self.lemma = lemma

"""
Gpred value
"""
class GpredValue(BaseConcept):
    def __init__(self, value = None):
        self.ID = None
        self.value = value      
        
"""
Real predicate
"""
class RealPred(BaseConcept):
    def __init__(self, lemma='', pos='', sense=''):
        self.ID = None
        self.lemma = lemma
        self.pos = pos
        self.sense = sense
        self.dmrs_nodeID = -1
    
"""
    Link between DMRS node
""" 
class Link(BaseConcept):
    """
    Link object constructor
    """
    def __init__(self, fromNode = None, toNode = None, post = None, rargname = None):
        self.ID = None
        self.fromNodeID = -1
        self.toNodeID = -1
        self.dmrsID = None
        
        self.fromNode = fromNode # From node
        self.toNode = toNode # To node
        self.post = post
        self.rargname = rargname
        
        
    def __str__(self):
        
        return "DMRS-Link:[Node: {fromNode}] => [Node: {toNode}] Post={post} Rargname={rargname}".format(fromNode=self.fromNode.nodeid, toNode=self.toNode.nodeid, post=self.post, rargname=self.rargname)

"""
Post of a Link
"""
class Post(BaseConcept):
    def __init__(self, value = None):
        self.ID = None
        self.value = value
        self.dmrs_linkID = -1
    
    def __str__(self):
        return self.value

"""
Rargname (of a Link)
""" 
class Rargname(BaseConcept):
    def __init__(self, value = None):
        self.ID = None
        self.value = value
        self.dmrs_linkID = -1

    def __str__(self):
        return self.value
        
