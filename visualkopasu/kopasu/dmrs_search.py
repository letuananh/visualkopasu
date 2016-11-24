'''
A simple DMRS search engine 
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
from collections import deque
import threading
import time

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


class QueryLink:
    def __init__(self, post=None, rargname=None, from_node=None, to_node=None, text=''):
        self.post = post
        self.rargname = rargname
        self.from_node = from_node
        self.to_node = to_node
        self.text = text
    
    def __str__(self):
        return "--post=%s / rargname=%s)--" % (self.post, self.rargname)

    def to_query(self, dmrs_filter_query=None):
        query = None
        params = None
        
        from_node_query = self.from_node.to_condition('fromnode') if self.from_node is not None else None
        to_node_query = self.to_node.to_condition('tonode') if self.to_node is not None else None
        if self.post is None and self.rargname is None and from_node_query is None and to_node_query is None:
            return None # no query info
        else:
            query = '''
            SELECT DISTINCT link.dmrsID
            FROM dmrs_link_index link
            '''
            if from_node_query: query += " ,dmrs_node_index fromnode "
            if to_node_query: query += " ,dmrs_node_index tonode "
            
            condition = ''
            params = []
            if dmrs_filter_query:
                condition += """ link.dmrsID IN (%s) """ % dmrs_filter_query.query
                params += dmrs_filter_query.params
                
            if from_node_query: 
                if len(condition) > 0:
                    condition += " AND "
                condition += " fromnode.nodeID = link.fromNodeID "
                condition += " AND " + from_node_query.query
                params += from_node_query.params
            if to_node_query: 
                if len(condition) > 0:
                    condition += " AND "
                condition += " tonode.nodeID = link.toNodeID "
                condition += " AND " + to_node_query.query
                params += to_node_query.params
            
            if len(condition) > 0:
                query += " WHERE " + condition
            
            return SQLiteQuery(query=query, params=params)      

class SQLiteQuery:
    def __init__(self, query, params):
        self.query = query
        self.params = params
        
    def __str__(self):
        return "Query: %s - Params: %s" % (self.query, self.params)
        
    def limit(self, limit=10000):
        self.query += " LIMIT ?"
        self.params += [limit]
        
class QueryNode:
    def __init__(self, carg=None, lemma=None, gpred=None, mode="?"):
        self.carg = carg
        self.lemma = lemma
        self.gpred = gpred
        self.mode = mode
        self.count = 0
        
    def __cmp__(self, other):
        return cmp(self.count, other.count)
    
    def __str__(self):
        if self.mode == '?':
            return 'Any node'
        elif self.mode == 'C':
            return "Mode='%s' Text='%s'" % (self.mode, self.carg)
        elif self.mode == 'G':
            return "Mode='%s' Text='%s'" % (self.mode, self.gpred)
        elif self.mode == 'L':
            return "Mode='%s' Text='%s'" % (self.mode, self.lemma)
        elif self.mode == 'U':
            return "Mode='%s' Lemma='%s' OR carg='%s'" % (self.mode, self.lemma, self.carg)
        else:
            return "Invalid node"

    def to_condition(self, table_name=None):
        query = None
        params = None
        if self.mode == '?':
            return None
        elif self.mode == 'C':
            query="%scarg=?" % (table_name + "." if table_name is not None else '')
            params=[self.carg]
        elif self.mode == 'G':
            query="%sgpred_valueID = (SELECT ID FROM dmrs_node_gpred_value WHERE value = ?)" % (table_name + "." if table_name is not None else '')
            params=[self.gpred]
        elif self.mode == 'L':
            query="%slemmaID = (SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma = ?)" % (table_name + "." if table_name is not None else '')
            params=[self.lemma]
        elif self.mode == 'U':
            query="(%scarg= ? OR %slemmaID = (SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma = ?))" % ((table_name + ".", table_name + ".") if table_name is not None else ('', ''))
            params=[self.carg, self.lemma]
        else:
            return None
        return SQLiteQuery(query=query, params=params)

    def to_query(self, dmrs_filter_query=None, field_to_get="dmrsID"):  
        query = None
        params = None
        if self.mode == '?':
            return None
        elif self.mode == 'C':
            query="SELECT DISTINCT %s FROM dmrs_node_index node WHERE %s carg=?"
            params=[self.carg]
        elif self.mode == 'G':
            query="SELECT DISTINCT %s FROM dmrs_node_index node WHERE %s gpred_valueID = (SELECT ID FROM dmrs_node_gpred_value WHERE value = ?)"
            params=[self.gpred]
        elif self.mode == 'L':
            query="SELECT DISTINCT %s FROM dmrs_node_index node WHERE %s lemmaID = (SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma = ?)"
            params=[self.lemma]
        elif self.mode == 'U':
            query="SELECT DISTINCT %s FROM dmrs_node_index node WHERE %s (carg= ? OR lemmaID = (SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma = ?))"
            params=[self.carg, self.lemma]
        else:
            return None

        query = self.to_condition()
        if query is not None:
            if dmrs_filter_query is not None:
                query.query = (' dmrsID IN (%s) AND ' % dmrs_filter_query.query) + query.query
                query.params = dmrs_filter_query.params + params 
            query.query = "SELECT DISTINCT %s FROM dmrs_node_index node WHERE " % field_to_get + query.query
            return query
        else:
            return None
        
class DMRSTextQuery:
    def __init__(self, query_string):
        self.query_string = query_string
        self.idx = 0
        self.parts = []
        
    def this_char(self):
        return self.query_string[self.idx]
    
    def is_eof(self):
        return self.idx == len(self.query_string)
    
    def increase_caret(self):
        self.idx += 1

class DMRSQueryParser:

    RESERVED_CHARS = [ '(', ')', ' ' ]

    @staticmethod
    def parse_raw(query_string):
        if not isinstance(query_string, str):
            return None
            
        query = DMRSTextQuery(query_string)
        parts = []
        #parts = filter(None, query.split(" "))
        
        while not query.is_eof():
            if query.this_char() == '(':
                parts.append('(')
                query.increase_caret()
            elif query.this_char() == ')':
                parts.append(')')
                query.increase_caret()
            elif query.this_char() == ' ':
                # ignore whitespace
                query.increase_caret()
            else:
                part = ''
                while not query.is_eof() and query.this_char() not in DMRSQueryParser.RESERVED_CHARS:
                    part+=query.this_char()
                    query.increase_caret()
                parts.append(part)
        
        return parts
        
    @staticmethod
    def parse(query_string):
        raw_parts = DMRSQueryParser.parse_raw(query_string)
        if raw_parts is None:
            logging.debug("Cannot parse raw")
            return None
        parts = deque(raw_parts)
        
        clauses = []
        clause = None
        # build clauses
        while len(parts) > 0:
            part = parts.popleft()
            if part == '(':
                if clause == None:
                    clause = []
                else:
                    # error
                    logging.debug("Invalid bracket")
                    return None
            elif part == ')':
                if len(clause) < 1 or len(clause) > 3:
                    logging.debug("Invalid clause (A clause must be either a node or a link)")
                    return None
                else:
                    clauses.append(clause)
                    clause = None
                    # next should be AND or OR
                    if len(parts) > 0:
                        next_part = parts.popleft()
                        if next_part.upper() not in ['AND']:
                            logging.debug("Invalid or missing boolean operator")
                            return None
                        if len(parts) == 0:
                            logging.debug("Boolean keyword at the end of the query")
                            return None
            else:
                if clause is not None:
                    clause.append(part)
                else:
                    # standalone without bracket -> assume a node clause
                    clauses.append([part])
                    # next should be AND or OR
                    if len(parts) > 0:
                        next_part = parts.popleft()
                        if next_part.upper() not in ['AND']:
                            logging.debug("Invalid or missing boolean operator")
                            return None
                        if len(parts) == 0:
                            logging.debug("Boolean keyword at the end of the query")
                            return None
                    #logging.debug("Invalid clause (missing bracket ?)")
                    #return None
        # we shouldn't have any clause left in the queue
        if clause != None:
            logging.debug("Incompleted query")
            return None
        return clauses
    
    @staticmethod
    def find_lemma_id(lemma):
        return lemma
        
    @staticmethod
    def find_gpred_id(gpred):
        return gpred
    
    @staticmethod
    def parse_node(node, id_only=False):
        query_node = None
        if node == "?":
            # select all
            query_node = QueryNode(mode="?")
            pass
        elif node.startswith("C:"): #CARG search
            query_node = QueryNode(carg=node[2:], mode="C")
        elif node.startswith("L:"): #Lemma search
            query_node = QueryNode(lemma=node[2:], mode="L")
        elif node.startswith("G:"): #gpred
            query_node = QueryNode(gpred=node[2:], mode="G")
        elif len(node) > 0: # carg or lemma
            query_node = QueryNode(lemma=node, carg=node, mode="U")
            pass
        return query_node

    @staticmethod
    def parse_link(link_text, from_node=None, to_node=None):
        link = QueryLink(text=link_text, post=None, rargname=None, from_node=from_node, to_node=to_node)
        if link.text == "/":
            # general link
            pass
        elif link.text.startswith("/"):
            rargname = link.text[1:]
        elif link.text.endswith("/"):
            post = link.text[:-1]
        else:
            parts = link.text.split("/")
            if len(parts) != 2:
                logging.debug("Invalid link")
                return None
            post = parts[0]
            rargname = parts[1]
            
        return link
            
    @staticmethod
    def build_query_graph(clauses):
        for clause in clauses:
            if len(clause) == 1:
                logging.debug("Node clause: [%s]" % DMRSQueryParser.parse_node(clause[0]))
            elif len(clause) == 2:
                logging.debug("Node with link: [%s] -- (%s)" % (DMRSQueryParser.parse_node(clause[0]), DMRSQueryParser.parse_link(clause[1])))
            elif len(clause) == 3:
                logging.debug("Node link to another node: [%s] -- (%s) -- [%s]" % (DMRSQueryParser.parse_node(clause[0]), DMRSQueryParser.parse_link(clause[1]), DMRSQueryParser.parse_node(clause[2])))
            else:
                logging.debug("Invalid clause")
            pass

class LiteSearchEngine:
    
    def __init__(self, sqldao, limit=40000):
        # TODO: search multiple collections
        self.dao = sqldao
        self.limit = limit
    
    def count_node(self, query_nodes):
        if query_nodes is not None:
            q = None
            for node in query_nodes:
                if q == None:
                    q = node.to_query()
                else:
                    q = node.to_query(q)
                    
            if q is None:
                return -1
            q.query = "SELECT COUNT(*) FROM (%s LIMIT ?)" % q.query
            q.params = q.params + [self.limit]
            logging.debug(q)
            rows = self.dao.query(q)
            #logging.debug(rows)
            if rows and len(rows) == 1 and len(rows[0]):
                return rows[0][0]
        return -1
    
    def get_dmrs(self, dmrs_filter_query):
        query = SQLiteQuery(
            query = '''
            SELECT sentence.ID AS 'sentenceID', dmrs.interpretationID, sentence.text, sentence.ident AS 'sentence_ident', sentence.documentID
            FROM dmrs
                LEFT JOIN interpretation ON dmrs.interpretationID = interpretation.ID
                LEFT JOIN sentence ON interpretation.sentenceID = sentence.ID
            WHERE dmrs.ID IN (%s)
            LIMIT ?
            ''' % dmrs_filter_query.query
            ,params = dmrs_filter_query.params + [self.limit]
        )
        
        #logging.debug(query)
        rows = self.dao.query(query)
        #logging.debug(rows)
        return rows

    def search(self, query_text):
        clauses = DMRSQueryParser.parse(query_text)
        
        if clauses is None:
            raise Exception("Invalid query (%s)" % (query_text,))
            return None

        node_queries = []
        link_queries = []

        for clause in clauses:
            if len(clause) == 1:
                node_queries.append(DMRSQueryParser.parse_node(clause[0]))
                # logging.debug("Node clause: [%s]" % DMRSQueryParser.parse_node(clause[0]))
            elif len(clause) == 2:
                #print"Node with link: [%s] -- (%s)" % (DMRSQueryParser.parse_node(clause[0]), DMRSQueryParser.parse_link(clause[1]))
                # ignore for now
                pass
            elif len(clause) == 3:
                from_node = DMRSQueryParser.parse_node(clause[0])
                to_node = DMRSQueryParser.parse_node(clause[2])
                node_queries.append(from_node)
                node_queries.append(to_node)
                link = DMRSQueryParser.parse_link(clause[1], from_node=from_node, to_node=to_node)
                link_queries.append(link)
                #print"Node link to another node: [%s] -- (%s) -- [%s]" % (DMRSQueryParser.parse_node(clause[0]), DMRSQueryParser.parse_link(clause[1]), DMRSQueryParser.parse_node(clause[2]))
            else:
                #logging.debug("Invalid clause")
                pass

        #logging.debug("Before: ")
        # for node in node_queries: logging.debug(node)
        
        # optimize node query order
        for node in node_queries:
            node.count = self.count_node([node])
            if node.count == -1:
                logging.debug("remove %s" % (node,))
                node_queries.remove(node)
            # AND only optimization => any 0 will lead to nothing!
            if node.count == 0:
                logging.debug("empty %s" % (node,))
                return []
        node_queries.sort()
        
        n_query=None
        for node in node_queries:
            if n_query is None:
                n_query = node.to_query()
            else:
                n_query = node.to_query(n_query)
         
        l_query = None
        for link in link_queries:
            if l_query is None:
                l_query = link.to_query(n_query)
            else:
                next_query = link.to_query(n_query)
                l_query.query += " INTERSECT " + next_query.query
                l_query.params += next_query.params
        
        final_query = l_query if l_query is not None else n_query
        
        if final_query is not None:
            final_query.limit(self.limit)
            rows = self.get_dmrs(final_query)
            
            logging.debug("~" * 20)
            logging.debug(final_query)
            if rows:
                logging.debug("Total found results: %s" % len(rows))
            else:
                logging.debug("None was found")
            logging.debug("~" * 20)

            # Build search results
            results = self.dao.build_search_result(rows, True)
            if results:
                for res in results:
                    res.set_property("collection_name", self.dao.name)
            return results
        else:
            logging.debug("Cannot form query")
            return None

class SearchThread(threading.Thread):
    def __init__(self, engine, query):
        threading.Thread.__init__(self)
        self.engine = engine
        self.query = query
        self.results = None
    
    def run(self):
        logging.debug("Searching on database: %s\nQuery: %s\n\n" % (self.engine.dao.orm_manager.db_path, self.query))
        self.results = self.engine.search(self.query)

class SearchCluster():
    def __init__(self, engines=None, concurrent_threads=4, limit=10000):
        self.engines = []
        self.limit = limit
        self.concurrent_threads = concurrent_threads
        if engines:
            for engine in engines:
                self.engines.append(engine)
    
    def add(self, engine):
        self.engines.append(engine)
    
    def count_node(self, query_nodes):
        logging.debug("\nCluster counting: %s\n" % (", ".join([str(node) for node in query_nodes])))
        results = 0
        for engine in self.engines:
            logging.debug("\nSearching on engine: %s\n" % engine.dao.name)
            result = engine.count_node(query_nodes)
            if result is not None and result > -1:
                results += result
            if results > self.limit:
                return results
            else:
                logging.debug("Found %d so far ..." % results)
        return results
    
    def search(self, query):
        # Create search threads
        threads = []
        results = []
        for engine in self.engines:
            threads.append(SearchThread(engine, query))
        
        # Start search threads
        
        while len(threads) > 0:
            running_threads = []
            if self.concurrent_threads == 0: # all
                for i in range(len(threads)):
                    running_threads.append(threads.pop())
            elif self.concurrent_threads > 0: # all
                for i in range(self.concurrent_threads):
                    if len(threads) > 0: running_threads.append(threads.pop())
            else:
                running_threads.append(threads.pop())
            
            for thread in running_threads:
                thread.start()
            # Wait until all searches are finished
            for thread in running_threads:
                logging.debug("Waiting for %s to reply" % thread.engine.name)
                thread.join()
                # Aggregate results
                if thread.results is not None:
                    results += thread.results
            if len(results) > self.limit:
                return results
            logging.debug("%s more clusters to be search" % len(threads))
        # Done!
        return results
