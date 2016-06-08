#!/usr/bin/python
'''
Demo DMRS query tool
@author: Le Tuan Anh
'''

# Copyright 2013, Le Tuan Anh (tuananh.ke@gmail.com)
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

import unicodedata
import sys
import bisect

from config import VisualKopasuConfiguration as vkconfig

from visualkopasu.kopasu.dao import DocumentDAO
from visualkopasu.kopasu.dmrs_search import LiteSearchEngine, SearchCluster
from visualkopasu.kopasu.dmrs_search import DMRSQueryParser

def writeline(a_str):
    if isinstance(a_str, str):
        print(a_str)
    else:
        print(unicodedata.normalize('NFKD', a_str).encode('ascii','ignore'))

def header(a_str):
    writeline("*" * 80)
    writeline(a_str)
    writeline("*" * 80)

def analyse_query(q):
    c = DMRSQueryParser.parse(q)
    writeline("-" * 80)
    writeline("Query: %s" % q)
    writeline("-" * 80)
    DMRSQueryParser.build_query_graph(c)
    writeline("")

def getDAO(dbname=None):
    root = vkconfig.CORPORA_FOLDER
    corpus = vkconfig.CORPUS
    if dbname is None:
        dbname = vkconfig.DEFAULT_DB_NAME
    doc = DocumentDAO.getDAO(DocumentDAO.SQLITE3, {'root': root, 'corpus': corpus, 'dbname': dbname, 'fill_cache' : False})    
    return doc

def search(engine, query_text):
    header(query_text)
    results = engine.search(query_text)
    if results is not None: 
        for res in results: 
            writeline(('[DB: %s]:' % res.dbname + unicode(res)))
        writeline("Total results: %s" % len(results))
    else:
        writeline("Query failed")

def demo():
    q1 = "(L:and    NEQ/L-INDEX      bazaar) AND (and /L-INDEX bazaar)"
    analyse_query(q1)
    q2 = "(? / bazaar) AND (? / cathedral) AND (?) AND (and / )"
    analyse_query(q2)
    
    header("DEMO SEARCH CLUSTER")
    cluster = build_cluster()
    results = cluster.search("Torvalds")
    if len(results) > 0:
        for res in results:
            writeline(unicode(res))
    else:
        writeline("Cluster search result: None was found")
    
    #dao = getDAO()
    #engine = LiteSearchEngine(dao)
    
    '''
    # Test DAO
    corpora = dao.getCorpora()
    for corpus in corpora:
        writeline(corpus)
        corpus.documents = dao.getDocumentOfCorpus(corpus.ID)
        for doc in corpus.documents:
            writeline(" -> Doc: %s" % doc.name)
    '''
    
    # Test counting
    a_node = DMRSQueryParser.parse_node('the')
    l = cluster.count_node([a_node])
    writeline("Node: %s - Count: %s" % (a_node, l))
    
    a_node = DMRSQueryParser.parse_node('L:the')
    l = cluster.count_node([a_node])
    writeline("Node: %s - Count: %s" % (a_node, l))
    
    a_node = DMRSQueryParser.parse_node('C:the')
    l = cluster.count_node([a_node])
    writeline("Node: %s - Count: %s" % (a_node, l))

    a_node = DMRSQueryParser.parse_node('G:named_rel')
    l = cluster.count_node([a_node])
    writeline("Node: %s - Count: %s" % (a_node, l))
    
    a_node = DMRSQueryParser.parse_node('language')
    l = cluster.count_node([a_node])
    writeline("Node: %s - Count: %s" % (a_node, l))
    
    a_node = DMRSQueryParser.parse_node('the')
    b_node = DMRSQueryParser.parse_node('language')
    l = cluster.count_node([b_node, a_node])
    writeline("Node: [%s, %s] - Count: %s" % (b_node, a_node, l))
        
    query = "computational and linguistics"
    search(cluster, query)
    
    query = 'Sheffield AND (computational / linguistics)'
    search(cluster, query)

    query = "(Sheffield / ?)"
    search(cluster, query)
    
    query = "(? / Sheffield)"
    search(cluster, query)
    
    query = "the"
    search(cluster, query)  

def build_cluster():
    #engine1 = LiteSearchEngine(getDAO('aclX'))
    #engine2 = LiteSearchEngine(getDAO('aclY'))
    #engine3 = LiteSearchEngine(getDAO('redwoods_active_indexed'))
    #cluster = SearchCluster()
    #cluster.add(engine1)
    #cluster.add(engine2)
    #cluster.add(engine3)
    
    cluster = SearchCluster(
    [
        LiteSearchEngine(getDAO('corpora_acl8'))
        ,LiteSearchEngine(getDAO('redwoods_active_indexed'))
    ])
    
    print("Intialising search cluster")
    #cluster = SearchCluster(concurrent_threads=0)
    #for i in range(49):
    #   engine = LiteSearchEngine(getDAO('corpora_acl%d' % (i+1)), limit=1000)
    #   print("Connected to DB: %s" % (engine.dao.orm_manager.db_path))
    #   cluster.add(engine) 
    return cluster

def main():
    cluster = build_cluster()
    query = raw_input("Enter a query: ")
    while len(query) > 0:
        search(cluster, query)
        query = raw_input("Enter a query: ")
    pass

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'demo':
        demo()      
    elif len(sys.argv) == 2 and sys.argv[1] == 'test':
        from kopasu.dmrs_search import QueryNode
        nodes=[]
        
        q4=QueryNode(lemma="D",mode="L")
        q4.count=4
        
        q5=QueryNode(lemma="E",mode="L")
        q5.count=4
        
        q1=QueryNode(lemma="A",mode="L")
        q1.count=31
        
        q2=QueryNode(lemma="B",mode="L")
        q2.count=22
        
        q3=QueryNode(lemma="C",mode="L")
        q3.count=13
        
        nodes = [q1, q2, q3, q4, q5]
        nodes.sort()
        
        for node in nodes:
            writeline(node)
        pass
    else:
        main()
    
    pass
