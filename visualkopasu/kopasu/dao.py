'''
Data access layer for VisualKopasu project.
@author: Le Tuan Anh
'''

# Copyright 2016, Le Tuan Anh (tuananh.ke@gmail.com)
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

import os.path
import logging
from visualkopasu.util import getLogger
from .models import Corpus
from .models import Document
from .models import Sentence
from .models import Interpretation
from .models import DMRS
from .models import ParseRaw
from .models import Node
from .models import Sense
from .models import SortInfo
from .models import NodeIndex
from .models import Link
from .models import LinkIndex
from .models import GpredValue
from .models import Lemma


from .liteorm import ORMInfo, LiteORM
from .liteorm import DBContext

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

logger = getLogger('visko.dao')


class CorpusORMSchema(object):
    def __init__(self, db_path):
        self.db_path = db_path
        self.orm_manager = LiteORM(db_path)
        # 0: table column | 1: object property
        self.Corpus = ORMInfo('corpus', ['ID', 'name'], Corpus(), orm_manager=self.orm_manager)
        self.Document = ORMInfo('document', ['ID', 'name', 'corpusID'], Document(), orm_manager=self.orm_manager)
        self.Sentence = ORMInfo('sentence', ['ID', 'ident', 'text', 'documentID'], Sentence(), orm_manager=self.orm_manager)
        self.Interpretation = ORMInfo('interpretation', ['ID', ['ident', 'rid'], 'mode', 'sentenceID'], Interpretation(), orm_manager=self.orm_manager)
        self.DMRS = ORMInfo('dmrs', ['ID', 'ident', 'cfrom', 'cto', 'surface', 'interpretationID'], DMRS(), orm_manager=self.orm_manager)
        self.ParseRaw = ORMInfo('parse_raw', ['ID', 'ident', 'text', 'rtype', 'interpretationID'], ParseRaw(), orm_manager=self.orm_manager)
        # Node related tables
        self.Node = ORMInfo('dmrs_node',
                            [
                                'ID',
                                ['nodeID', 'nodeid'],
                                'cfrom',
                                'cto',
                                'surface',
                                'base',
                                'carg',
                                'dmrsID',
                                'rplemmaID',
                                'rppos',
                                'rpsense',
                                'gpred_valueID',
                                'synsetid',
                                'synset_score'
                            ],
                            Node(), orm_manager=self.orm_manager)
        self.SortInfo = ORMInfo('dmrs_node_sortinfo',
                                [
                                    'ID',
                                    'cvarsort',
                                    ['number', 'num'],
                                    ['person', 'pers'],
                                    ['gender', 'gend'],
                                    ['sentence_force', 'sf'],
                                    'tense',
                                    'mood',
                                    ['pronoun_type', 'prontype'],
                                    ['progressive', 'prog'],
                                    ['perfective_aspect', 'perf'],
                                    'ind',
                                    'dmrs_nodeID'
                                ],
                                SortInfo(), orm_manager=self.orm_manager)
        self.GpredValue = ORMInfo('dmrs_node_gpred_value', ['ID', 'value'], GpredValue(), orm_manager=self.orm_manager)
        self.Lemma = ORMInfo('dmrs_node_realpred_lemma', ['ID', 'lemma'], Lemma(), orm_manager=self.orm_manager)
        # Link related tables
        self.Link = ORMInfo('dmrs_link',
                            [
                                'ID',
                                'fromNodeID',
                                'toNodeID',
                                'dmrsID',
                                'post',
                                'rargname'],
                            Link(), orm_manager=self.orm_manager)

        self.NodeIndex = ORMInfo('dmrs_node_index', ['nodeID', 'carg', 'lemmaID', 'pos', 'sense', 'gpred_valueID', 'dmrsID', 'documentID'], NodeIndex(), orm_manager=self.orm_manager)
        # self.LinkIndex = ORMInfo('dmrs_link_index', ['linkID', 'fromNodeID', 'toNodeID', 'post', 'rargname', 'dmrsID', 'documentID'], LinkIndex(), orm_manager=self.orm_manager)
# TODO: Split the SQL code to a separate ORM engine


class ObjectCache():
    '''
    A simple ORM cache
    @auto_fill: Auto select all objects to cache when the cache is created
    '''
    def __init__(self, manager, orm_config, cache_by_field="value", auto_fill=True):
        self.cacheMap = {}
        self.cacheMapByID = {}
        self.manager = manager
        self.orm_config = orm_config
        self.cache_by_field = cache_by_field
        if auto_fill:
            instances = self.orm_config.select()
            if instances != None:
                for instance in instances:
                    self.cache(instance)

    def cache(self, instance):
        if instance:
            key = instance.__dict__[self.cache_by_field]
            if key not in self.cacheMap:
                self.cacheMap[key] = instance
            else:
                logger.debug(("Cache error: key [%s] exists!" % key))
                
            key = instance.__dict__[self.orm_config.columnID]
            if key not in self.cacheMapByID:
                self.cacheMapByID[key] = instance
            else:
                logger.debug(("Cache error: ID [%s] exists!" % key))

    def getByValue(self, value, new_object=None, context=None):
        if value not in self.cacheMap:
            # insert a new record
            if new_object is None:
                # try to select from database first
                results = self.orm_config.select(condition="%s=?" % self.cache_by_field, args=[value])
                if results is None or len(results) != 1:
                    # logger.debug("Cache: There is no instance with value = [%s] - Attempting to create one ..." % value)
                    new_object = self.orm_config.create_instance()
                    new_object.__dict__[self.cache_by_field] = value
                    self.orm_config.save(new_object, update_back=True, context=context)
                else:
                    new_object = results[0]  # Use the object from DB
            self.cache(new_object)
        return self.cacheMap[value]

    def getByID(self, ID):
        if ID not in self.cacheMapByID:
            # select from database
            obj = self.orm_config.getByID(ID)
            self.cache(obj)
        return self.cacheMapByID[ID]


class SQLiteCorpusCollection(object):
    def __init__(self, path):
        self.path = path

    def getCorpusDAO(self, collection_name, auto_fill=False):
        collection_db_path = os.path.join(self.path, collection_name + '.db')
        return SQLiteCorpusDAO(collection_db_path, collection_name, auto_fill)


class SQLiteCorpusDAO(CorpusORMSchema):
    
    def __init__(self, db_path, name, auto_fill):
        super().__init__(db_path)
        self.name = name
        self.lemmaCache = ObjectCache(self.orm_manager, self.Lemma, "lemma", auto_fill=auto_fill)
        self.gpredCache = ObjectCache(self.orm_manager, self.GpredValue, "value", auto_fill=auto_fill)

    def getCorpora(self):
        return self.Corpus.select()

    def getCorpus(self, corpus_name):
        return self.Corpus.select('name=?', [corpus_name])

    def getCorpusByID(self, corpusID):
        return self.Corpus.select('ID=?', (corpusID,))[0]

    def createCorpus(self, corpus_name, context=None):
        return self.Corpus.save(Corpus(corpus_name), context=context)

    def saveDocument(self, a_document, context=None):
        self.Document.save(a_document, context=context)

    def getDocumentOfCorpus(self, corpusID):
        return self.Document.select('corpusID=?', [corpusID])

    def getDocuments(self):
        return self.Document.select()

    def getDocument(self, docID):
        return self.Document.getByID(docID)

    def getDocumentByName(self, doc_name):
        return self.Document.select('name=?', [doc_name])

    def getSentences(self, docID):
        return self.Sentence.select('documentID=?', (docID,))

    def buildContext(self):
        context = DBContext(self.orm_manager.getConnection())
        context.cur.execute("PRAGMA cache_size=80000000")
        context.cur.execute("PRAGMA journal_mode=MEMORY")
        context.cur.execute("PRAGMA temp_store=MEMORY")
        # context.cur.execute("PRAGMA count_changes=OFF")
        return context

    def query(self, query_obj):
        return self.orm_manager.selectRows(query_obj.query, query_obj.params)

    def saveSentence(self, a_sentence, context=None, auto_flush=True):
        """
        Complicated queries
        """
        if a_sentence is None:
            raise Exception("Sentence object cannot be None")
        if context is None:
            context = self.buildContext()
        if not a_sentence.ID:
            self.Sentence.save(a_sentence, context=context)
            # save interpretations
            for interpretation in a_sentence.interpretations:
                # Update sentenceID
                interpretation.sentenceID = a_sentence.ID
                self.Interpretation.save(interpretation, context=context)
                # Save raw
                for raw in interpretation.raws:
                    raw.interpretationID = interpretation.ID
                    self.ParseRaw.save(raw, context=context)
                # Save DMRS
                for dmrs in interpretation.dmrs:
                    dmrs.interpretationID = interpretation.ID
                    self.DMRS.save(dmrs, context=context)
                    # save nodes
                    for node in dmrs.nodes:
                        nodeindex = NodeIndex()
                        node.dmrsID = dmrs.ID
                        # save realpred
                        if node.rplemma:
                            # Escape lemma
                            lemma = self.lemmaCache.getByValue(node.rplemma, context=context)
                            node.rplemmaID = lemma.ID
                            nodeindex.lemmaID = lemma.ID
                            nodeindex.pos = node.rppos
                            nodeindex.sense = node.rpsense
                        # save gpred
                        if node.gpred:
                            gpred_value = self.gpredCache.getByValue(node.gpred, context=context)
                            node.gpred_valueID = gpred_value.ID
                            nodeindex.gpred_valueID = gpred_value.ID
                        # save sense
                        if node.sense:
                            node.synsetid = node.sense.synsetid
                            node.synset_score = node.sense.score
                        self.Node.save(node, context=context)
                        # save sortinfo
                        node.sortinfo.dmrs_nodeID = node.ID
                        self.SortInfo.save(node.sortinfo, context=context)
                        # other nodeindex info
                        nodeindex.nodeID = node.ID
                        if node.carg:
                            nodeindex.carg = node.carg
                        nodeindex.dmrsID = dmrs.ID
                        nodeindex.documentID = a_sentence.documentID
                        self.NodeIndex.save(nodeindex, context=context)
                    # save links
                    for link in dmrs.links:
                        link.dmrsID = dmrs.ID
                        link.fromNodeID = link.fromNode.ID
                        link.toNodeID = link.toNode.ID
                        if link.rargname is None:
                            link.rargname = ''
                        # build link index
                        linkindex = LinkIndex()
                        linkindex.linkID = link.ID
                        linkindex.fromNodeID = link.fromNode.ID
                        linkindex.toNodeID = link.toNode.ID
                        linkindex.post = link.post
                        linkindex.rargname = link.rargname
                        linkindex.dmrsID = dmrs.ID
                        linkindex.documentID = a_sentence.documentID
                        self.Link.save(link, context)
            if auto_flush:
                context.flush()
        else:
            # update sentence
            pass
        # Select sentence
        return a_sentence
    
    def searchInterpretations(self, mode=None, rargname=None, post=None, lemma=None, limit=50):
        query = '''
        SELECT interpretation.ID as interpretationID, sentenceID as sentenceID, text FROM interpretation
        LEFT JOIN sentence ON sentenceID = sentence.ID
        {condition}
        '''
        
        link_conditions_template = '''
        interpretation.ID IN
            (SELECT interpretationID from dmrs WHERE 
            dmrs.ID IN ( SELECT dmrsID 
                    FROM dmrs_link 
                        LEFT JOIN dmrs_link_post ON dmrs_link_post.dmrs_linkID = dmrs_link.ID
                        LEFT JOIN dmrs_link_rargname ON dmrs_link_rargname.dmrs_linkID = dmrs_link.ID
                    {link_conditions} LIMIT ?)
            )
        '''
        node_conditions_template = '''
        interpretation.ID IN
            (SELECT interpretationID from dmrs WHERE 
            dmrs.ID IN ( SELECT dmrsID 
                    FROM dmrs_node_realpred AS "realpred" 
                        LEFT JOIN dmrs_node ON realpred.dmrs_nodeID = dmrs_node.ID 
                    {node_conditions} LIMIT ?)
            )
        '''
        interpretation_condition = ''
        link_conditions = ''
        node_conditions = ''
        conditions = []
        params = []

        # Interpretation condition
        if mode:
            interpretation_condition += 'mode = ?'
            conditions.append(interpretation_condition)
            params.append(mode)

        # Node condition
        if lemma:
            node_conditions += ' realpred.lemmaID = (SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma=?) '
            params.append(lemma)
        if len(node_conditions) > 0:
            node_conditions = 'WHERE ' + node_conditions
            node_conditions = node_conditions_template.format(node_conditions=node_conditions)
            conditions.append(node_conditions)
            
        # Link condition
        if rargname:
            link_conditions += ' dmrs_link_rargname.value = ?'
            params.append(rargname)
        if post:
            link_conditions += ' dmrs_link_post.value = ?'
            params.append(post)
        if len(link_conditions) > 0:
            link_conditions = 'WHERE ' + link_conditions
            link_conditions = link_conditions_template.format(link_conditions=link_conditions)
            conditions.append(link_conditions)
            
        # Final condition
        condition = ' AND '.join(conditions)
        if len(condition) > 0:
            condition = 'WHERE ' + condition

        params.append(limit)
        logger.debug(("Query: %s" % query.format(condition=condition)))
        logger.debug(("Params: %s" % params))
        rows = self.orm_manager.selectRows(query.format(condition=condition), params)
        # logger.debug("rows: %s" % rows)
        if rows:
            logger.debug(("Found: %s presentation(s)" % len(rows)))
        else:
            logger.debug("None was found!")

        sentences = []
        sentences_by_id = {}
        for row in rows:
            interpretationID = row['interpretationID']
            sentenceID = row['sentenceID']
            if sentenceID not in sentences_by_id:
                # update interpretation
                a_interpretation = Interpretation(ID=interpretationID)
                # self.getInterpretation(a_interpretation)
                sentences_by_id[sentenceID].interpretations.append(a_interpretation)
            else:
                a_sentence = self.getSentence(sentenceID, interpretationIDs=[], skip_details=True)
                a_sentence.interpretations = []
                a_interpretation = Interpretation(ID=interpretationID)
                a_sentence.interpretations.append(a_interpretation)
                sentences.append(a_sentence)
                sentences_by_id[sentenceID] = a_sentence
            # sentences.append(a_sentence)
        
        logger.debug(("Sentence count: %s" % len(sentences)))
        return sentences
    
    def build_search_result(self, rows, no_more_query=False):
        if rows:
            logger.debug(("Found: %s presentation(s)" % len(rows)))
        else:
            logger.debug("None was found!")
            return []
        sentences = []
        sentences_by_id = { }
        for row in rows:
            interpretationID = row['interpretationID']
            sentenceID = row['sentenceID']
            sentence_ident = row['sentence_ident']
            text = row['text']
            documentID = row['documentID']
            if sentenceID in sentences_by_id:
                # update interpretation
                a_interpretation = Interpretation(ID=interpretationID)
                # self.getInterpretation(a_interpretation)
                sentences_by_id[sentenceID].interpretations.append(a_interpretation)
            else:
                if no_more_query:
                    a_sentence=Sentence(ident=sentence_ident, text=text, documentID=documentID)
                    a_sentence.ID=sentenceID
                else:
                    a_sentence = self.getSentence(sentenceID, interpretationIDs=[], skip_details=True)
                a_sentence.interpretations = []
                a_interpretation = Interpretation(ID=interpretationID)
                a_sentence.interpretations.append(a_interpretation)
                sentences.append(a_sentence)
                sentences_by_id[sentenceID] = a_sentence
            #sentences.append(a_sentence)
        
        logger.debug(("Sentence count: %s" % len(sentences)))
        return sentences
    
    def getLemma(self, lemma):
        lemmata = self.Lemma.select("lemma=?", [lemma])
        if len(lemmata) == 1:
            return lemmata[0]
        else:
            return None
                
    def searchByLemma(self, lemma, limit=1000):
        lemma = self.getLemma(lemma)
        if lemma is None:
            return []
        else:
            logger.debug(lemma)
            lemmaID = lemma.ID
            
        query = '''
            SELECT DISTINCT interpretation.sentenceID, dmrs.interpretationID, sentence.text
            FROM dmrs_node_realpred "realpred"
                LEFT JOIN dmrs_node "node" ON node.ID = realpred.dmrs_nodeID
                LEFT JOIN dmrs ON node.dmrsID = dmrs.ID
                LEFT JOIN interpretation ON dmrs.interpretationID = interpretation.ID
                LEFT JOIN sentence ON interpretation.sentenceID = sentence.ID
            WHERE realpred.lemmaID = ?
            LIMIT ?
        '''
        params = [lemmaID, limit]

        logger.debug(("Query: %s" % query))
        logger.debug(("Params: %s" % params))
        rows = self.orm_manager.selectRows(query, params)
        return self.build_search_result(rows)
    
    def searchByCarg(self, carg, limit=1000):
        query ='''
            SELECT DISTINCT interpretation.sentenceID,dmrs.interpretationID, sentence.text
            FROM dmrs_node "node"
                LEFT JOIN dmrs ON node.dmrsID = dmrs.ID
                LEFT JOIN interpretation ON dmrs.interpretationID = interpretation.ID
                LEFT JOIN sentence ON interpretation.sentenceID = sentence.ID
            WHERE node.carg = ?
            LIMIT ?
        '''
        params = [carg, limit]
        
        logger.debug(("Query: %s" % query))
        logger.debug(("Params: %s" % params))
        rows = self.orm_manager.selectRows(query, params)
        return self.build_search_result(rows)

    def getInterpretation(self, a_interpretation):
        # retrieve all DMRSes
        self.DMRS.select('interpretationID=?', [a_interpretation.ID], a_interpretation.dmrs)
        for a_dmrs in a_interpretation.dmrs:                
            # retrieve all nodes
            self.Node.select('dmrsID=?', [a_dmrs.ID], a_dmrs.nodes)
            for a_node in a_dmrs.nodes:
                # retrieve sortinfo
                list_sortinfo = self.SortInfo.select('dmrs_nodeID=?', [a_node.ID])
                if len(list_sortinfo) == 1:
                    a_node.sortinfo = list_sortinfo[0]
                # retrieve realpred
                if a_node.rplemmaID:
                    a_node.rplemma = self.lemmaCache.getByID(int(a_node.rplemmaID)).lemma
                # retrieve gpred
                if a_node.gpred_valueID:
                    a_node.gpred = self.gpredCache.getByID(int(a_node.gpred_valueID)).value
                # create sense object
                if a_node.synsetid:
                    sense_info = Sense()
                    sense_info.synsetid = a_node.synsetid
                    sense_info.score = a_node.synset_score
                    sense_info.pos = a_node.synsetid[-1]
                    a_node.sense = sense_info
            # retrieve all links
            self.Link.select('dmrsID=?', [a_dmrs.ID], a_dmrs.links)
            # update link node
            for a_link in a_dmrs.links:
                a_link.fromNode = a_dmrs.getNodeById(a_link.fromNodeID, True)[0]
                a_link.toNode = a_dmrs.getNodeById(a_link.toNodeID, True)[0]
        return a_interpretation

    def saveParseRaw(self, a_raw, context=None):
        self.ParseRaw.save(a_raw, context=context)

    def get_raw(self, interpretationID, interpretation=None):
        raws = self.ParseRaw.select('interpretationID=?', (interpretationID,))
        if interpretation is not None:
            for raw in raws:
                raw.interpretationID = interpretation.ID
                interpretation.raws.append(raw)
        return raws

    def getSentence(self, sentenceID, mode=None, interpretationIDs=None, skip_details=False, get_raw=True):
        a_sentence = self.Sentence.getByID(str(sentenceID))
        if a_sentence is not None:
            # retrieve all interpretations
            conditions = 'sentenceID=?'
            params = [a_sentence.ID]
            if mode:
                conditions += ' AND mode=?'
                params.append(mode)
            if interpretationIDs and len(interpretationIDs) > 0:
                conditions += ' AND ID IN ({params_holder})'.format(params_holder=",".join((["?"] * len(interpretationIDs))))
                params = params + interpretationIDs
            self.Interpretation.select(conditions, params, a_sentence.interpretations)
            for a_interpretation in a_sentence.interpretations:
                if get_raw:
                    self.get_raw(a_interpretation.ID, a_interpretation)
                if not skip_details:
                    self.getInterpretation(a_interpretation)
        else:
            logging.debug("No sentence with ID={} was found".format(sentenceID))
        # Return
        return a_sentence
