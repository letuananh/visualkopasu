"""
A simple DMRS search engine
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

import logging
from collections import deque
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def getLogger():
    return logging.getLogger(__name__)


class SQLiteQuery:
    def __init__(self, query, params=None):
        self.query = query
        self.params = params if params else []

    def __str__(self):
        return "Query: %s - Params: %s" % (self.query, self.params)

    def limit(self, limit=10000):
        self.query += " LIMIT ?"
        self.params += [limit]

    def select(self, ctx):
        return ctx.select(self.query, self.params)

    def select_single(self, ctx):
        return ctx.select_single(self.query, self.params)

    def select_scalar(self, ctx):
        return ctx.select_scalar(self.query, self.params)


class QuerySurface:
    def __init__(self, mode='^', text=''):
        self.mode = mode
        self.text = text

    def __repr__(self):
        return "QuerySurface(mode={}, text={})".format(repr(self.mode), repr(self.text))

    def __str__(self):
        return "{}:{}".format(self.mode, self.text)

    def to_query(self):
        query = """SELECT sid FROM word WHERE (lemma like ?) OR (word like ?)"""
        params = [self.text, self.text]
        return SQLiteQuery(query=query, params=params)


class QueryLink:
    def __init__(self, post=None, rargname=None, from_node=None, to_node=None, text=''):
        self.post = post
        self.rargname = rargname
        self.from_node = from_node
        self.to_node = to_node
        self.text = text

    def __str__(self):
        return "--(post=%s/rargname=%s)--" % (self.post, self.rargname)

    def to_query(self, dmrs_filter_query=None):
        query = None
        params = None

        from_node_query = self.from_node.to_condition('fromnode') if self.from_node is not None else None
        to_node_query = self.to_node.to_condition('tonode') if self.to_node is not None else None
        if self.post is None and self.rargname is None and from_node_query is None and to_node_query is None:
            return None  # no query info
        else:
            query = 'SELECT DISTINCT link.dmrsID FROM dmrs_link link\n'
            if from_node_query:
                query += " LEFT JOIN dmrs_node AS fromnode ON link.fromnodeID =  fromnode.ID \n"
            if to_node_query:
                query += " LEFT JOIN dmrs_node AS tonode ON link.tonodeID = tonode.ID \n"
            conditions = []
            params = []
            if dmrs_filter_query:
                conditions.append(" link.dmrsID IN (%s)" % dmrs_filter_query.query)
                params += dmrs_filter_query.params
            # filter by rargname and post
            if self.post:
                conditions.append(" link.post = ?")
                params.append(self.post)
            if self.rargname:
                conditions.append(" link.rargname = ?")
                params.append(self.rargname)
            if from_node_query:
                conditions.append(from_node_query.query)
                params += from_node_query.params
            if to_node_query:
                conditions.append(to_node_query.query)
                params += to_node_query.params

            if len(conditions) > 0:
                query += " WHERE " + ' \nAND '.join(conditions)

            return SQLiteQuery(query=query, params=params)


class QueryNode:
    def __init__(self, carg=None, lemma=None, gpred=None, synsetID=None, mode="?"):
        self.carg = carg
        self.lemma = lemma
        self.gpred = gpred
        self.mode = mode
        self.synsetID = synsetID.strip() if synsetID else synsetID
        self.count = 0

    def __lt__(self, other):
        return self.count < other.count

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
        elif self.mode == 'S':
            return "Mode='%s' SynsetID='%s'" % (self.mode, self.synsetID)
        else:
            return "Invalid node"

    def to_condition(self, table_name=None):
        query = None
        params = None
        if self.mode == '?':
            return None
        elif self.mode == 'C':
            query = "lower({tn}carg)=lower(?)".format(tn=table_name + "." if table_name is not None else '')
            params = [self.carg.lower()]
        elif self.mode == 'G':
            query = "{tn}gpred_valueID = (SELECT ID FROM dmrs_node_gpred_value WHERE value = ?)".format(tn=table_name + "." if table_name is not None else '')
            params = [self.gpred]
        elif self.mode == 'L':
            query = "{tn}rplemmaID = (SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma = ?)".format(tn=table_name + "." if table_name is not None else '')
            params = [self.lemma]
        elif self.mode == 'S':
            query = "{tn}synsetid = ?".format(tn=table_name + "." if table_name is not None else '')
            params = [self.synsetID]
        elif self.mode == 'U':
            query = "(lower({tn}carg)=? OR {tn}rplemmaID=(SELECT ID FROM dmrs_node_realpred_lemma WHERE lemma = ?))".format(tn=table_name + "." if table_name is not None else '')
            params = [self.carg.lower(), self.lemma]
        else:
            raise Exception("Invalid mode ({})".format(self.mode))
        return SQLiteQuery(query=query, params=params)

    def to_query(self, dmrs_filter_query=None, field_to_get="dmrsID"):
        query = self.to_condition()
        if dmrs_filter_query is not None:
            query.query = ' dmrsID IN {dids} AND {q}'.format(dids=dmrs_filter_query.query, q=query.query)
            query.params = dmrs_filter_query.params + query.params
        query.query = "SELECT DISTINCT %s FROM dmrs_node node WHERE " % field_to_get + query.query
        return query


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

    RESERVED_CHARS = ['(', ')', ' ']

    @staticmethod
    def parse_raw(query_string):
        if not isinstance(query_string, str):
            return None
        query = DMRSTextQuery(query_string)
        parts = []
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
                    part += query.this_char()
                    query.increase_caret()
                parts.append(part)
        return parts

    @staticmethod
    def parse(query_string):
        raw_parts = DMRSQueryParser.parse_raw(query_string)
        if raw_parts is None:
            logger.debug("Cannot parse raw")
            return None
        parts = deque(raw_parts)

        clauses = []
        clause = None
        # build clauses
        while len(parts) > 0:
            part = parts.popleft()
            if part == '(':
                if clause is None:
                    clause = []
                else:
                    # error
                    logger.debug("Invalid bracket")
                    return None
            elif part == ')':
                if len(clause) < 1 or len(clause) > 3:
                    logger.debug("Invalid clause (A clause must be either a node or a link)")
                    return None
                else:
                    clauses.append(clause)
                    clause = None
                    # next should be AND or OR
                    if len(parts) > 0:
                        next_part = parts.popleft()
                        if next_part.upper() not in ['AND']:
                            logger.debug("Invalid or missing boolean operator")
                            return None
                        if len(parts) == 0:
                            logger.debug("Boolean keyword at the end of the query")
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
                            logger.debug("Invalid or missing boolean operator")
                            return None
                        if len(parts) == 0:
                            logger.debug("Boolean keyword at the end of the query")
                            return None
        # we shouldn't have any clause left in the queue
        if clause is not None:
            logger.debug("Incompleted query")
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
        elif node.startswith("C:"):  # CARG search
            query_node = QueryNode(carg=node[2:], mode="C")
        elif node.startswith("L:"):  # Lemma search
            query_node = QueryNode(lemma=node[2:], mode="L")
        elif node.startswith("G:"):  # gpred
            query_node = QueryNode(gpred=node[2:], mode="G")
        elif node.startswith("S:"):  # gpred
            query_node = QueryNode(synsetID=node[2:], mode="S")
        elif len(node) > 0:          # carg or lemma
            query_node = QueryNode(lemma=node, carg=node, mode="U")
            pass
        return query_node

    @staticmethod
    def parse_link(link_text, from_node_text=None, to_node_text=None):
        from_node = DMRSQueryParser.parse_node(from_node_text)
        to_node = DMRSQueryParser.parse_node(to_node_text)
        link = QueryLink(text=link_text, post=None, rargname=None, from_node=from_node, to_node=to_node)
        if link.text == "/":
            # general link
            pass
        elif link.text.startswith("/"):
            link.rargname = link.text[1:]
        elif link.text.endswith("/"):
            link.post = link.text[:-1]
        else:
            parts = link.text.split("/")
            if len(parts) != 2:
                logger.debug("Invalid link")
                return None
            link.post = parts[0]
            link.rargname = parts[1]
        return link


class LiteSearchEngine:

    def __init__(self, sqldao, limit=40000):
        # TODO: search multiple collections
        self.dao = sqldao
        self.limit = limit

    def count_node(self, query_nodes):
        if query_nodes is not None:
            q = None
            for node in query_nodes:
                if q is None:
                    q = node.to_query()
                else:
                    q = node.to_query(q)
            if q is None:
                return -1
            q.query = "SELECT COUNT(*) FROM (%s LIMIT ?)" % q.query
            q.params = q.params + [self.limit]
            q.select(self.dao.ctx())
        return -1

    def get_dmrs(self, dmrs_filter_query):
        query = SQLiteQuery(query="""SELECT sentence.ID AS 'sentID', dmrs.readingID, sentence.text, sentence.ident AS 'sentence_ident', sentence.docID, document.name as doc_name, corpus.name as corpus_name, corpus.ID as corpusID
            FROM dmrs
                LEFT JOIN reading ON dmrs.readingID = reading.ID
                LEFT JOIN sentence ON reading.sentID = sentence.ID
                LEFT JOIN document ON sentence.docID = document.ID
                LEFT JOIN corpus ON document.corpusID = corpus.ID
            WHERE dmrs.ID IN (%s)
            LIMIT ?""" % dmrs_filter_query.query,
                            params=dmrs_filter_query.params + [self.limit])
        logger.debug(query)
        rows = query.select(self.dao.ctx())
        return rows

    def get_sent(self, sent_filter_query):
        query_txt = """SELECT sentence.ID AS 'sentID', NULL AS readingID, sentence.text, sentence.ident AS 'sentence_ident', sentence.docID, document.name as doc_name, corpus.name as corpus_name, corpus.ID as corpusID
            FROM sentence
            LEFT JOIN document ON sentence.docID = document.ID
            LEFT JOIN corpus ON document.corpusID = corpus.ID
            WHERE sentID IN ({})
        LIMIT ?""".format(sent_filter_query.query)
        query = SQLiteQuery(query=query_txt, params=sent_filter_query.params + [self.limit])
        logger.debug(query)
        rows = query.select(self.dao.ctx())
        return rows

    def search_by_ident(self, ident):
        q = """SELECT sentence.ID AS 'sentID', dmrs.readingID, sentence.text, sentence.ident AS 'sentence_ident', sentence.docID, document.name as doc_name, corpus.name as corpus_name, corpus.ID as corpusID
            FROM sentence
                LEFT JOIN reading ON reading.ID = sentence.ID
                LEFT JOIN dmrs ON reading.ID = dmrs.readingID
                LEFT JOIN document ON sentence.docID = document.ID
                LEFT JOIN corpus ON document.corpusID = corpus.ID
            WHERE sentence.ident = ?
            LIMIT ?"""
        query = SQLiteQuery(query=q, params=[ident, self.limit])
        logger.debug(query)
        rows = query.select(self.dao.ctx())
        return rows

    def search(self, query_text):
        getLogger().debug("Query: {}".format(query_text))
        clauses = DMRSQueryParser.parse(query_text)
        if clauses is None:
            raise Exception("Invalid query (%s)" % (query_text,))
            return None
        elif len(clauses) == 1 and len(clauses[0]) == 1 and clauses[0][0].startswith('#'):
            # search by SID
            rows = self.search_by_ident(clauses[0][0][1:])
            # Build search results
            results = self.dao.build_search_result(rows)
            for res in results:
                setattr(res, "collection_name", self.dao.name)
            return results

        node_queries = []
        link_queries = []
        surface_queries = []

        for clause in clauses:
            if len(clause) == 1:
                if clause[0].startswith('^:') or clause[0].startswith('＾：'):
                    getLogger().debug("Surface search: {}".format(clause))
                    surface_queries.append(QuerySurface(mode='^', text=clause[0][2:]))
                else:
                    node_queries.append(DMRSQueryParser.parse_node(clause[0]))
            elif len(clause) == 3:
                link = DMRSQueryParser.parse_link(clause[1], clause[0], clause[2])
                link_queries.append(link)
            else:
                raise Exception("Invalid clause ({})".format(clause))
                pass

        # optimize node query order
        # for node in node_queries:
        #     node.count = self.count_node([node])
        #     if node.count == -1:
        #         logger.debug("remove %s" % (node,))
        #         node_queries.remove(node)
        #     # AND only optimization => any 0 will lead to nothing!
        #     if node.count == 0:
        #         logger.debug("empty %s" % (node,))
        #         return []
        # node_queries.sort()
        # final query
        query = None
        rows = []
        for clause in node_queries + link_queries:
            if query is None:
                query = clause.to_query()
            else:
                next_query = clause.to_query()
                query.query += " INTERSECT " + next_query.query
                query.params += next_query.params
        if query:
            query.limit(self.limit)
            rows += self.get_dmrs(query)
        # query surfaces
        squery = None
        for clause in surface_queries:
            if squery is None:
                squery = clause.to_query()
            else:
                next_query = clause.to_query()
                squery.query += " INTERSECT " + next_query.query
                squery.params += next_query.params
        if squery:
            getLogger().debug("Surface query: {}".format(squery))
            squery.limit(self.limit)
            rows += self.get_sent(squery)
        # Build search results
        results = self.dao.build_search_result(rows)
        for res in results:
            setattr(res, "collection_name", self.dao.name)
        return results


class SearchThread(threading.Thread):
    def __init__(self, engine, query):
        threading.Thread.__init__(self)
        self.engine = engine
        self.query = query
        self.results = None

    def run(self):
        logger.debug("Searching on database: %s\nQuery: %s\n\n" % (self.engine.dao.orm_manager.db_path, self.query))
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
        logger.debug("\nCluster counting: %s\n" % (", ".join([str(node) for node in query_nodes])))
        results = 0
        for engine in self.engines:
            logger.debug("\nSearching on engine: %s\n" % engine.dao.name)
            result = engine.count_node(query_nodes)
            if result is not None and result > -1:
                results += result
            if results > self.limit:
                return results
            else:
                logger.debug("Found %d so far ..." % results)
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
            if self.concurrent_threads == 0:  # all
                for i in range(len(threads)):
                    running_threads.append(threads.pop())
            elif self.concurrent_threads > 0:  # all
                for i in range(self.concurrent_threads):
                    if len(threads) > 0:
                        running_threads.append(threads.pop())
            else:
                running_threads.append(threads.pop())
            for thread in running_threads:
                thread.start()
            # Wait until all searches are finished
            for thread in running_threads:
                logger.debug("Waiting for %s to reply" % thread.engine.name)
                thread.join()
                # Aggregate results
                if thread.results is not None:
                    results += thread.results
            if len(results) > self.limit:
                return results
            logger.debug("%s more clusters to be search" % len(threads))
        # Done!
        return results
