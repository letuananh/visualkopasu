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

import logging
from delphin.mrs import Pred
from chirptext.texttaglib import TaggedSentence, Token
from coolisf.model import Sentence as ISFSentence

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

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class Corpus(object):
    '''
    A corpus wrapper
    '''
    def __init__(self, name='', title=''):
        self.ID = None
        self.name = name
        self.title = title
        self.documents = []
        pass


class Document(object):

    def __init__(self, name='', corpusID=None, title='', grammar=None, tagger=None, parse_count=None, lang=None):
        self.ID = None
        self.name = name
        self.corpusID = corpusID
        self.title = title if title else name
        self.grammar = grammar
        self.tagger = tagger
        self.parse_count = parse_count
        self.lang = lang
        self.corpus = None
        self.sentences = []
        pass

    def __str__(self):
        return "Doc#{id}".format(id=self.ID)


class Sentence(object):

    GOLD = 1
    ERROR = 2

    def __init__(self, ident=0, text='', documentID=None):
        self.ID = None
        self.ident = ident
        self.text = text
        self.documentID = documentID
        self.flag = None
        self.comment = None
        self.corpus = None
        self.collection = None
        self.readings = []
        self.filename = None
        # human annotation layer
        self.words = []
        self.concepts = []
        self.cmap = {}  # concept.ID -> concept objects
        self.wmap = {}  # word.ID -> word objects

    def import_tags(self, tagged_sent):
        ''' Import a chirptext.texttaglib.TaggedSentence as human annotations '''
        # add words
        word_map = {}
        for idx, w in enumerate(tagged_sent):
            wobj = Word(widx=idx, word=w.label, lemma=w.lemma, pos=w.pos, cfrom=w.cfrom, cto=w.cto, sent=self)
            if w.comment:
                wobj.comment = w.comment
            word_map[w] = wobj
            self.words.append(wobj)
        # add concepts
        for idx, c in enumerate(tagged_sent.concepts):
            cobj = Concept(cidx=idx, clemma=c.clemma, tag=c.tag, sent=self)
            cobj.comment = c.comment if c.comment else ''
            cobj.flag = c.flag if c.flag else ''
            self.concepts.append(cobj)
            # add cwlinks
            for w in c.words:
                wobj = word_map[w]
                cobj.words.append(wobj)

    @property
    def shallow(self):
        if not self.words:
            return None
        else:
            tsent = TaggedSentence(self.text)
            for word in self.words:
                tk = tsent.add_token(word.word, word.cfrom, word.cto)
                if word.lemma:
                    tk.tag(word.lemma, tagtype=Token.LEMMA)
                if word.pos:
                    tk.tag(word.pos, tagtype=Token.POS)
                if word.comment:
                    tk.tag(word.comment, tagtype=Token.COMMENT)
            for concept in self.concepts:
                wids = [self.words.index(w) for w in concept.words]
                c = tsent.tag(concept.clemma, concept.tag, *wids)
                if concept.flag:
                    c.flag = concept.flag
                if concept.comment:
                    c.comment = concept.comment
                pass
            return tsent
        pass

    def getInactiveReading(self):
        return [repr for repr in self.readings if repr.mode == "inactive"]

    def getActiveReading(self):
        return [repr for repr in self.readings if repr.mode == "active"]

    def has_raw(self):
        ''' Check if there is at least one readings and
        all readings has raw inside'''
        has_raw = len(self) > 0
        for i in self.readings:
            has_raw = has_raw and len(i.raws) > 0
        return has_raw

    def is_error(self):
        return self.flag == Sentence.ERROR

    def __len__(self):
        return len(self.readings)

    def __getitem__(self, key):
        return self.readings[key]

    def __iter__(self):
        return iter(self.readings)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "({col}\{cor}\{did}\Sent#{i})`{t}`".format(col=self.collection, cor=self.corpus, did=self.documentID, i=self.ident, t=self.text)
    
    def to_isf(self):
        ''' Convert Visko Sentence to ISF sentence'''
        isfsent = ISFSentence(self.text, str(self.ID))
        isfsent.shallow = self.shallow
        for i in self:
            # we should use XML first as it has sense information
            xml_raw = i.find_raw(ParseRaw.XML)
            if xml_raw is not None:
                logger.debug("Using DMRS XML raw")
                p = isfsent.add(dmrs_xml=xml_raw.text)
                p.ID = i.ID  # parse ID should have the same ID as reading obj
                p.ident = i.rid
            else:
                # try MRS
                mrs_raw = i.find_raw(ParseRaw.MRS)
                if mrs_raw is not None:
                    p = isfsent.add(mrs_str=mrs_raw.text)
                    p.ID = i.ID  # parse ID should have the same ID as reading obj
                    p.ident = i.rid
                else:
                    # TODO:build XML from DMRSes?
                    pass
        return isfsent


class ParseRaw(object):

    JSON = 'json'
    XML = 'xml'
    MRS = 'mrs'  # MRS string - e.g. ACE output

    def __init__(self, text='', ID=None, ident='', rtype=XML):
        self.ID = ID
        self.ident = ident
        self.text = text
        self.rtype = rtype

    def __repr__(self):
        txt = self.text if len(self.text) < 50 else self.text[:25] + '...' + self.text[-25:]
        return "[{}:{}]".format(self.rtype, txt.strip())

    def __str__(self):
        # return repr(self)
        return self.text


class Reading(object):

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
        return u"Reading [ID={rid}, mode={mode}]".format(rid=self.rid, mode=self.mode)

    def add_raw(self, text='', ID=None, ident='', rtype=ParseRaw.XML):
        self.raws.append(ParseRaw(text, ID, ident, rtype))

    def find_raw(self, rtype):
        for r in self.raws:
            if r.rtype == rtype:
                return r
        return None


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


class DMRS(object):
    """
    DMRS object default constructor
    """
    def __init__(self, ident='', cfrom=-1, cto=-1, surface=''):
        self.ID = None
        self.ident = ident
        self.cfrom = cfrom
        self.cto = cto
        self.surface = surface
        self.readingID = None

        # Nodes and links might be indexed for faster access
        self.nodes = []
        self.links = []

    def getNodeById(self, nodeid, use_record_ID=False):
        if use_record_ID:
            return [node for node in self.nodes if node.ID == nodeid]
        else:
            return [node for node in self.nodes if node.nodeid == nodeid]

    def getLink(self, fromid=None, toid=None):
        return [link for link in self.links if ((not fromid) or link.fromNode.nodeid == fromid) and ((not toid) or link.toNode.nodeid == toid)]

    def __str__(self):
        nodes = [str(n) for n in self.nodes if str(n.nodeid) != '0']
        links = [str(l) for l in self.links]

        return "dmrs {{\n{nl}\n}} ".format(ident=self.ident, cfrom=self.cfrom, to=self.cto, surface=self.surface, nl=';\n'.join(nodes + links))


class Node(object):
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

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.gpred:
            pred = self.gpred
        else:
            pred = Pred.realpred(self.rplemma, self.rppos, self.rpsense if self.rpsense else None).short_form()
        sensetag = ''
        if self.sense:
            sensetag = ' synsetid={} synset_lemma={} synset_score={}'.format(self.sense.synsetid, self.sense.lemma.replace(' ', '+'), self.sense.score)
        carg = '("{}")'.format(self.carg) if self.carg else ''
        return "{nodeid} [{pred}<{cfrom}:{cto}>{carg} {sortinfo}{sensetag}]".format(nodeid=self.nodeid, cfrom=self.cfrom, cto=self.cto, sortinfo=self.sortinfo, sensetag=sensetag, pred=pred, carg=carg)


class Sense(object):
    def __init__(self, lemma='', pos='', synsetid='', score=0):
        self.lemma = lemma
        self.pos = pos
        self.synsetid = synsetid
        self.score = score


class SortInfo(object):
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
        valdict = [(k, self.__dict__[k]) for k in ['num', 'pers', 'gend', 'sf', 'tense', 'mood', 'prontype', 'prog', 'perf', 'ind'] if self.__dict__[k]]
        if self.cvarsort:
            return self.cvarsort + ' ' + ' '.join(('{}={}'.format(k.upper(), str(v)) for (k, v) in valdict))
        else:
            return ' '.join(('{}={}'.format(k.upper(), str(v)) for (k, v) in valdict))


class GpredValue(object):
    """
    Gpred (grammar predicate) value
    """
    def __init__(self, value=None):
        self.ID = None
        self.value = value

    def __str__(self):
        return "#{}({})".format(self.ID, self.value)


class Lemma(object):
    """
    Lemma of Real pred
    """
    def __init__(self, lemma=None):
        self.ID = None
        self.lemma = lemma

    def __str__(self):
        return "#{}({})".format(self.ID, self.lemma)


class Link(object):
    """
    DMRS links
    """
    def __init__(self, fromNode=None, toNode=None, post='', rargname=''):
        self.ID = None
        self.fromNodeID = -1
        self.toNodeID = -1
        self.dmrsID = None
        self.fromNode = fromNode
        self.toNode = toNode
        self.post = post
        self.rargname = rargname

    def __str__(self):
        return "{fromNode}:{rargname}/{post} -> {toNode}".format(fromNode=self.fromNode.nodeid, toNode=self.toNode.nodeid, post=self.post if self.post else '', rargname=self.rargname if self.rargname else '')


class Word(object):
    """
    Human annotator layer: Words
    """
    def __init__(self, widx=-1, word='', lemma='', pos='', cfrom=-1, cto=-1, sent=None):
        self.ID = None
        if sent:
            self.sid = sent.ID
            self.sent = sent
        else:
            self.sid = -1
            self.sent = None
        self.widx = widx
        self.word = word
        self.pos = pos
        self.lemma = lemma
        self.cfrom = cfrom
        self.cto = cto
        self.comment = ''

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "`{w}`<{cf}:{ct}>".format(w=self.word, cf=self.cfrom, ct=self.cto)


class Concept(object):
    """
    Human annotator layer: Concepts
    """
    def __init__(self, cidx=-1, clemma=None, tag=None, sent=None):
        self.ID = None
        if sent:
            self.sid = sent.ID
            self.sent = sent
        else:
            self.sid = -1
            self.sent = None
        self.cidx = cidx
        self.clemma = clemma
        self.tag = tag
        self.flag = None
        self.comment = ''
        self.words = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "`{lemma}`:{tag}".format(lemma=self.clemma, tag=self.tag)


class CWLink(object):
    """
    Human annotator layer: Word-Concept Links
    """
    def __init__(self, wid=-1, cid=-1):
        self.wid = wid
        self.cid = cid

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "c#{}->w#{}".format(self.cid, self.wid)
