'''
Data access layer for VisualKopasu project.
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

import gzip
import os.path
import copy
import sqlite3
from xml.etree import ElementTree as ETree

from .models import *
from .liteorm import ORMInfo, LiteORM
from .liteorm import DBContext

class DocumentDAO:
    XML = 1
    SQLITE3 = 2
    NEO4J = 3
    
    @staticmethod
    def getDAO(daoType, config):
        path = os.path.join(config['root'], config['dbname']) if 'dbname' in config and config['dbname'] is not None else os.path.join(config['root'], config['corpus'])
        if daoType == DocumentDAO.XML:
            if os.path.isfile(path):
                # zipped
                from .zippedxmldao import ZippedXMLDocumentDAO
                return ZippedXMLDocumentDAO(config)
            else:
                # folder-based DAO
                from .xmldao import XMLDocumentDAO
                return XMLDocumentDAO(config)
        elif daoType == DocumentDAO.SQLITE3:
            return SQLiteDocumentDAO(config)
        return None # only support XML at the momment

class VisualKopasuORMConfig:
    def __init__(self, orm_manager):
        self.orm_manager = orm_manager
        # 0: table column | 1: object property
        self.Corpus = ORMInfo('corpus', ['ID', 'name'], Corpus(), orm_manager=self.orm_manager)
        self.Document = ORMInfo('document', ['ID', 'name', 'corpusID'], Document(), orm_manager=self.orm_manager)
        self.Sentence = ORMInfo('sentence', [ 'ID', 'ident', 'text', 'documentID' ], Sentence(), orm_manager=self.orm_manager)
        self.Interpretation = ORMInfo('interpretation',['ID', ['ident', 'rid'], 'mode', 'sentenceID'], Interpretation(), orm_manager=self.orm_manager)
        self.DMRS = ORMInfo('dmrs', ['ID', 'ident', 'cfrom', 'cto', 'surface', 'interpretationID'], DMRS(), orm_manager=self.orm_manager)
        # Node related tables
        self.Node = ORMInfo('dmrs_node', ['ID', ['nodeID', 'nodeid'], 'cfrom', 'cto', 'surface', 'base', 'carg', 'dmrsID'], Node(), orm_manager=self.orm_manager)
        self.SortInfo = ORMInfo('dmrs_node_sortinfo'
                        , ['ID'
                            , 'cvarsort' 
                            , ['number', 'num']
                            , ['person', 'pers']
                            , ['gender', 'gend']
                            , ['sentence_force', 'sf']
                            , 'tense'
                            , 'mood'
                            , ['pronoun_type', 'prontype']
                            , ['progressive', 'prog']
                            , ['perfective_aspect', 'perf']
                            , 'ind'
                            , 'dmrs_nodeID'
                        ]
                        , SortInfo(),orm_manager=self.orm_manager)  
        self.Gpred = ORMInfo('dmrs_node_gpred', ['ID', ['gpred_valueID','value'], 'dmrs_nodeID'], Gpred(),orm_manager=self.orm_manager) 
        self.RealPred = ORMInfo('dmrs_node_realpred', ['ID', ['lemmaID','lemma'], 'pos', 'sense', 'dmrs_nodeID'], RealPred(),orm_manager=self.orm_manager)  
        self.GpredValue = ORMInfo('dmrs_node_gpred_value', ['ID', 'value'], GpredValue(), orm_manager=self.orm_manager)
        self.Lemma = ORMInfo('dmrs_node_realpred_lemma', ['ID', 'lemma'], Lemma(), orm_manager=self.orm_manager)
        # Link related tables
        self.Link = ORMInfo('dmrs_link', ['ID', 'fromNodeID', 'toNodeID', 'dmrsID'], Link(),orm_manager=self.orm_manager)
        self.Post = ORMInfo('dmrs_link_post', ['ID', 'value', 'dmrs_linkID'], Post(),orm_manager=self.orm_manager)
        self.Rargname = ORMInfo('dmrs_link_rargname', ['ID', 'value', 'dmrs_linkID'], Rargname(),orm_manager=self.orm_manager)
        
        self.NodeIndex = ORMInfo('dmrs_node_index', ['nodeID', 'carg', 'lemmaID', 'pos', 'sense', 'gpred_valueID', 'dmrsID', 'documentID'], NodeIndex(), orm_manager=self.orm_manager)
        self.LinkIndex = ORMInfo('dmrs_link_index', ['linkID', 'fromNodeID', 'toNodeID', 'post', 'rargname', 'dmrsID', 'documentID'], LinkIndex(), orm_manager=self.orm_manager)
# TODO: Split the SQL code to a separate ORM engine

'''
A simple ORM cache
@auto_fill: Auto select all objects to cache when the cache is created
'''
class ObjectCache():
    def __init__(self, manager, orm_config, cache_by_field = "value", auto_fill=True):
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
                print(("Cache error: key [%s] exists!" % key))
                
            key = instance.__dict__[self.orm_config.columnID]
            if key not in self.cacheMapByID:
                self.cacheMapByID[key] = instance
            else:
                print(("Cache error: ID [%s] exists!" % key))
            
    def getByValue(self, value, new_object = None, context = None):
        if value not in self.cacheMap:
            # insert a new record
            if new_object is None:
                # try to select from database first
                results = self.orm_config.select(condition = "%s=?" % self.cache_by_field, args = [value])
                if results is None or len(results) != 1:
                    #print("Cache: There is no instance with value = [%s] - Attempting to create one ..." % value)
                    new_object = self.orm_config.create_instance()
                    new_object.__dict__[self.cache_by_field] = value
                    self.orm_config.save(new_object, update_back = True, context = context)
                else:
                    new_object = results[0] # Use the object from DB
            self.cache(new_object)
        return self.cacheMap[value]
    
    def getByID(self, ID):
        if ID not in self.cacheMapByID:
            # select from database
            obj = self.orm_config.getByID(ID)
            self.cache(obj)
        return self.cacheMapByID[ID]
                
class SQLiteDocumentDAO():
    
    def __init__(self, config):
        self.config = config
        # Set database path in LiteORM
        if 'dbname' in config and config['dbname'] is not None and len(config['dbname']) > 0:
            db_path = os.path.join(self.config['root'], self.config['dbname'] + ".db")
        else:
            self.config['dbname'] = self.config['corpus']
            db_path = os.path.join(self.config['root'], self.config['corpus'] + ".db")
        self.orm_manager = LiteORM(db_path) 
        self.ORM = VisualKopasuORMConfig(self.orm_manager)
        if 'fill_cache' in config:
            self.lemmaCache = ObjectCache(self.orm_manager, self.ORM.Lemma, "lemma", auto_fill=config['fill_cache'])
            self.gpredCache = ObjectCache(self.orm_manager, self.ORM.GpredValue, "value", auto_fill=config['fill_cache'])
        else:
            self.lemmaCache = ObjectCache(self.orm_manager, self.ORM.Lemma, "lemma")
            self.gpredCache = ObjectCache(self.orm_manager, self.ORM.GpredValue, "value")

    def getCorpora(self):
        return self.ORM.Corpus.select()

    def getCorpus(self, corpus_name):
        return self.ORM.Corpus.select('name=?', [corpus_name])

    def saveCorpus(self, a_corpus, context=None):
        self.ORM.Corpus.save(a_corpus, context=context)

    def saveDocument(self, a_document, context=None):
        self.ORM.Document.save(a_document, context=context)

    def getDocumentOfCorpus(self, corpusID):
        return self.ORM.Document.select('corpusID=?', [corpusID])

    def getDocuments(self):
        return self.ORM.Document.select()

    def getDocument(self, docID):
        return self.ORM.Document.getByID(docID)

    def getDocumentByName(self, doc_name):
        return self.ORM.Document.select('name=?', [doc_name])
    
    def getSentences(self, docID):
        return self.ORM.Sentence.select('documentID=?', (docID,))

    def buildContext(self):
        context = DBContext(self.orm_manager.getConnection())
        context.cur.execute("PRAGMA cache_size=80000000")
        context.cur.execute("PRAGMA journal_mode=MEMORY")
        context.cur.execute("PRAGMA temp_store=MEMORY")
        #context.cur.execute("PRAGMA count_changes=OFF")
        return context

    def query(self, query_obj):
        return self.orm_manager.selectRows(query_obj.query, query_obj.params)

    """
    Complicated queries
    """
            
    def saveSentence(self, a_sentence, context=None, auto_flush=True):
        if context is None:
            context = self.buildContext()
        
        if not a_sentence.ID:
            self.ORM.Sentence.save(a_sentence, context=context)
            # save interpretations
            for interpretation in a_sentence.interpretations:
                # Update sentenceID
                interpretation.sentenceID = a_sentence.ID
                self.ORM.Interpretation.save(interpretation,context=context)
                # Save DMRS
                for dmrs in interpretation.dmrs:
                    dmrs.interpretationID = interpretation.ID
                    self.ORM.DMRS.save(dmrs,context=context)
                    
                    # save nodes
                    for node in dmrs.nodes:
                        nodeindex = NodeIndex()
                        #self.NodeIndex = ORMInfo('dmrs_node_index', ['nodeID', 'carg', 'lemmaID', 'pos', 'sense', 'gpred_valueID', 'dmrsID', 'documentID'], NodeIndex(), orm_manager=self.orm_manager)                     
                        node.dmrsID = dmrs.ID
                        self.ORM.Node.save(node, context=context)
                        # node index
                        nodeindex.nodeID = node.ID
                        if node.carg: nodeindex.carg = node.carg
                        nodeindex.dmrsID = dmrs.ID
                        nodeindex.documentID = a_sentence.documentID
                        # save sortinfo
                        node.sortinfo.dmrs_nodeID = node.ID
                        self.ORM.SortInfo.save(node.sortinfo,context=context)
                        # save realpred
                        if node.realpred:
                            # Escape lemma
                            if node.realpred.lemma:
                                lemma = self.lemmaCache.getByValue(node.realpred.lemma, context=context)
                                node.realpred.lemma = lemma.ID # TODO: Fix this
                                nodeindex.lemmaID = lemma.ID
                            node.realpred.dmrs_nodeID = node.ID
                            self.ORM.RealPred.save(node.realpred,context)
                            if node.realpred.pos: nodeindex.pos = node.realpred.pos
                            if node.realpred.sense: nodeindex.sense = node.realpred.sense
                        # save gpred
                        if node.gpred:
                            if node.gpred.value:
                                gpred_value = self.gpredCache.getByValue(node.gpred.value, context=context)
                                node.gpred.value = gpred_value.ID # TODO: fix this
                                nodeindex.gpred_valueID = gpred_value.ID
                            node.gpred.dmrs_nodeID = node.ID
                            self.ORM.Gpred.save(node.gpred,context)
                        # index node
                        self.ORM.NodeIndex.save(nodeindex, context=context)
                    # end fore
                    
                    # save links
                    for link in dmrs.links:
                        linkindex = LinkIndex()
                        #self.LinkIndex = ORMInfo('dmrs_link_index', ['linkID', 'fromNodeID', 'toNodeID', 'post', 'rargname', 'dmrsID', 'documentID'], LinkIndex(), orm_manager=self.orm_manager)
                        link.dmrsID = dmrs.ID
                        link.fromNodeID = link.fromNode.ID
                        link.toNodeID = link.toNode.ID
                        self.ORM.Link.save(link,context)
                        # save post
                        link.post.dmrs_linkID = link.ID
                        self.ORM.Post.save(link.post,context)
                        # save rargname
                        link.rargname.dmrs_linkID = link.ID
                        self.ORM.Rargname.save(link.rargname,context)
                        # build link index
                        linkindex.linkID = link.ID
                        linkindex.fromNodeID = link.fromNode.ID
                        linkindex.toNodeID = link.toNode.ID
                        linkindex.post=link.post.value
                        linkindex.rargname=link.rargname.value
                        linkindex.dmrsID = dmrs.ID
                        linkindex.documentID = a_sentence.documentID
                        self.ORM.LinkIndex.save(linkindex, context=context)
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
        print(("Query: %s" % query.format(condition=condition)))
        print(("Params: %s" % params))
        rows = self.orm_manager.selectRows(query.format(condition=condition), params)
        # print("rows: %s" % rows)
        if rows:
            print(("Found: %s presentation(s)" % len(rows)))
        else:
            print("None was found!")
        
        sentences = []
        sentences_by_id = { }
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
            #sentences.append(a_sentence)
        
        print(("Sentence count: %s" % len(sentences)))
        return sentences
    
    def build_search_result(self, rows, no_more_query=False):
        if rows:
            print(("Found: %s presentation(s)" % len(rows)))
        else:
            print("None was found!")
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
        
        print(("Sentence count: %s" % len(sentences)))
        return sentences
    
    def getLemma(self, lemma):
        lemmata = self.ORM.Lemma.select("lemma=?", [lemma])
        if len(lemmata) == 1:
            return lemmata[0]
        else:
            return None
                
    def searchByLemma(self, lemma, limit=1000):
        lemma = self.getLemma(lemma)
        if lemma is None:
            return []
        else:
            print(lemma)
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

        print(("Query: %s" % query))
        print(("Params: %s" % params))
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
        
        print(("Query: %s" % query))
        print(("Params: %s" % params))
        rows = self.orm_manager.selectRows(query, params)
        return self.build_search_result(rows)
            
    def getInterpretation(self, a_interpretation):
        # retrieve all DMRSes
        self.ORM.DMRS.select('interpretationID=?', [a_interpretation.ID], a_interpretation.dmrs)
        for a_dmrs in a_interpretation.dmrs:                
            # retrieve all nodes
            self.ORM.Node.select('dmrsID=?', [a_dmrs.ID], a_dmrs.nodes)
            for a_node in a_dmrs.nodes:
                # retrieve sortinfo
                list_sortinfo = self.ORM.SortInfo.select('dmrs_nodeID=?', [a_node.ID])
                if len(list_sortinfo) == 1:
                    a_node.sortinfo = list_sortinfo[0]
                # retrieve realpred
                list_realpred = self.ORM.RealPred.select('dmrs_nodeID=?', [a_node.ID])
                if len(list_realpred) == 1:
                    a_node.realpred = list_realpred[0]
                    # replace lemma
                    a_node.realpred.lemma = self.lemmaCache.getByID(int(a_node.realpred.lemma)).lemma
                # retrieve gpred
                list_gpred = self.ORM.Gpred.select('dmrs_nodeID=?', [a_node.ID])
                if len(list_gpred) == 1:                    
                    a_node.gpred = list_gpred[0]
                    # replace gpred value
                    a_node.gpred.value = self.gpredCache.getByID(int(a_node.gpred.value)).value
            
            # retrieve all links
            self.ORM.Link.select('dmrsID=?', [a_dmrs.ID], a_dmrs.links)
            # update link node
            for a_link in a_dmrs.links:
                a_link.fromNode = a_dmrs.getNodeById(a_link.fromNodeID, True)[0]
                a_link.toNode = a_dmrs.getNodeById(a_link.toNodeID, True)[0]
                # get post
                list_post = self.ORM.Post.select('dmrs_linkID=?', [a_link.ID])
                if len(list_post) == 1:
                    a_link.post = list_post[0]
                # get rargname
                list_rargname = self.ORM.Rargname.select('dmrs_linkID=?', [a_link.ID])
                if len(list_rargname) == 1:
                    a_link.rargname = list_rargname[0]
        return a_interpretation

    def getSentence(self, sentenceID, mode = None, interpretationIDs = None, skip_details=None):
        a_sentence = self.ORM.Sentence.getByID(sentenceID)
        
        if a_sentence:
            # retrieve all interpretations
            conditions = 'sentenceID=?'
            params = [a_sentence.ID]
            if mode:
                conditions += ' AND mode=?'
                params.append(mode)
            if interpretationIDs and len(interpretationIDs) > 0:
                conditions += ' AND ID IN ({params_holder})'.format(params_holder=",".join((["?"] * len(interpretationIDs))))
                params = params + interpretationIDs
                
            self.ORM.Interpretation.select(conditions, params, a_sentence.interpretations)
            for a_interpretation in a_sentence.interpretations:
                if not skip_details:
                    self.getInterpretation(a_interpretation)
        # Return
        return a_sentence   

