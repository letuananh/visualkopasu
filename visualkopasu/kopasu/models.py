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

########################################################################

from .liteorm import SmartRecord

########################################################################

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2012, Visual Kopasu"
__credits__ = ["Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################


class Corpus(SmartRecord):
    '''
    A corpus wrapper
    '''
    def __init__(self, name=''):
        self.ID = None
        self.name = name
        self.documents = []
        pass


class Document(SmartRecord):
    
    def __init__(self, name='', corpusID=None):
        self.ID = None
        self.name = name
        self.corpusID = corpusID
        self.corpus = None
        self.sentences = []
        pass


class Sentence(SmartRecord):

    def __init__(self, ident=0, text='', documentID=None):
        self.ID = None
        self.ident = ident
        self.text = text
        self.documentID = documentID
        self.interpretations = []
        self.filename = None
        # self.dmrs = []
        # self.parseTrees = []

    def getInactiveInterpretation(self):
        return [repr for repr in self.interpretations if repr.mode == "inactive"]

    def getActiveInterpretation(self):
        return [repr for repr in self.interpretations if repr.mode == "active"]

    def __len__(self):
        return len(self.interpretations)

    def __getitem__(self, key):
        return self.interpretations[key]

    def __str__(self):
        return "[ID=" + self.ident + "]" + self.text


class Interpretation(SmartRecord):

    INACTIVE = 0
    ACTIVE = 1

    def __init__(self, rid='', mode='', ID=None, dmrs=None, trees=None, raws=None):
        self.ID = ID
        self.rid = rid
        self.mode = mode
        self.dmrs = dmrs if dmrs else list()
        self.parse_trees = trees if trees else list()
        self.sentenceID = None
        self.raws = raws if raws else list()

    def __str__(self):
        return u"Interpretation [ID={rid}, mode={mode}]".format(rid=self.rid, mode=self.mode)


class ParseRaw(SmartRecord):

    JSON = 'json'
    XML = 'xml'
    MRS = 'mrs'  # MRS string - e.g. ACE output

    def __init__(self, text='', ID=None, ident='', rtype=JSON):
        self.ID = ID
        self.ident = ident
        self.text = text
        self.rtype = rtype

    def __repr__(self):
        return str(self)

    def __str__(self):
        txt = self.text if len(self.text) < 50 else self.text[:25] + '...' + self.text[-25:]
        return "[{}:{}]".format(self.rtype, txt.strip())


class ParseTree:
    """
    Parse tree (synthetic tree)
    """
    def __init__(self, root, value=''):
        self.value = value
        self.root = root


class ParseNode:
    """
    A node of parse tree
    """
    def __init__(self, nodetype, value):
        self.nodetype = nodetype
        self.value = value
        self.children = []

    def __str__(self):
        return u"{type}: {value}".format(type=self.nodetype, value=self.value)


class DMRS(SmartRecord):
    """
    DMRS object default constructor
    """
    def __init__(self, ident='', cfrom=-1, cto=-1, surface=''):
        self.ID = None
        self.ident = ident
        self.cfrom = cfrom
        self.cto = cto
        self.surface = surface
        self.interpretationID = None

        # Nodes and links might be indexed for faster access
        self.nodes = []
        self.links = []

    def getNodeById(self, nodeid, use_record_ID=False):
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


class Node(SmartRecord):
    """
    Node object constructor
    """
    def __init__(self, nodeid=None, cfrom=-1, cto=-1, surface='', base='', carg=''):
        self.ID = None
        self.nodeid = nodeid
        self.cfrom = cfrom
        self.cto = cto
        self.surface = surface
        self.base = base
        self.carg = carg
        self.dmrsID = -1
        self.sortinfo = None
        # gpred
        self.gpred = None
        self.gpred_valueID = None
        # realpred
        self.rplemma = None
        self.rplemmaID = None
        self.rppos = None
        self.rpsense = None  # realpred sense
        self.sense = None
        self.synsetid = None
        self.synset_score = None

    def __str__(self):
        return u"DMRS-Node: [ id={nodeid} [{cfrom}:{cto}] SORT_INFO={{{sortinfo}}} PRED={{{pred}}} ]".format(nodeid=self.nodeid, cfrom=self.cfrom, cto=self.cto, sortinfo=self.sortinfo, pred=str(self.gpred) if self.gpred is not None else str(self.realpred))


class NodeIndex(SmartRecord):
    def __init__(self):
        self.nodeID = None
        self.carg = None
        self.lemmaID = None
        self.pos = None
        self.sense = None
        self.gpred_valueID = None
        self.dmrsID = None
        self.documentID = None


class LinkIndex(SmartRecord):
    def __init__(self):
        self.linkID = None
        self.fromNodeID = None
        self.toNodeID = None
        self.post = None
        self.rargname = None
        self.dmrsID = None
        self.documentID = None


class Sense(SmartRecord):
    def __init__(self, lemma='', pos='', synsetid='', score=0):
        self.lemma = lemma
        self.pos = pos
        self.synsetid = synsetid
        self.score = score


class SortInfo(SmartRecord):
    """
    sortinfo of a Node
    """
    def __init__(self, cvarsort='', num='', pers='', gend='', sf='', tense='', mood='', prontype='', prog='', perf='', ind=''):
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
        return str(',\t '.join('%s : %s' % (k, str(v)) for (k, v) in self.__dict__.items() if v))


class GpredValue(SmartRecord):
    """
    Gpred (grammar predicate) value
    """
    def __init__(self, value=None):
        self.ID = None
        self.value = value


class Lemma(SmartRecord):
    """
    Lemma of Real pred
    """
    def __init__(self, lemma=None):
        self.ID = None
        self.lemma = lemma


class Link(SmartRecord):
    """
    DMRS links
    """
    def __init__(self, fromNode=None, toNode=None, post=None, rargname=''):
        self.ID = None
        self.fromNodeID = -1
        self.toNodeID = -1
        self.dmrsID = None
        self.fromNode = fromNode
        self.toNode = toNode
        self.post = post
        self.rargname = rargname

    def __str__(self):
        return "DMRS-Link:[Node: {fromNode}] => [Node: {toNode}] Post={post} Rargname={rargname}".format(fromNode=self.fromNode.nodeid, toNode=self.toNode.nodeid, post=self.post, rargname=self.rargname)
