'''
Convert a document from XML-based format into SQLite3 format for VisualKopasu
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

from visualkopasu.kopasu.dao import *
from visualkopasu.kopasu.xmldao import *
import shutil

import csv, time, datetime
import sqlite3
import os
from visualkopasu.config import ViskoConfig as vkconfig
from visualkopasu.config import Biblioteca
class Timer:
    def __init__(self):
        self._start = time.time()
        self._end = time.time()
        self._runtime = 0
        
    def start(self):
        self._start = time.time()
    def end(self):
        self._end = time.time()
        return self
    
    def runtime(self):
        self._runtime = (self._end - self._start)
        return self._runtime
    def report(self):
        print("Runtime: %5.2f seconds" % self._runtime)

timer = Timer()

def readscript(filename):
    script_location = os.path.join(vkconfig.SETUP_SCRIPTS_ROOT, 'sqlite3', filename)
    return open(script_location, 'r').read()

'''
Prepare database
'''

def backup_database(location_target):
    print("Backing up existing database file ...")
    if os.path.isfile(location_target):
        i = 0
        backup_file = location_target + ".bak." + str(i)
        while os.path.isfile(backup_file):
            i = i + 1
            backup_file = location_target + ".bak." + str(i)
        
        print("Renaming file %s --> %s" % (location_target, backup_file))
        os.rename(location_target, backup_file)

def prepare_database(corpora_root, database_file):
    location = os.path.join(corpora_root, database_file + '_temp.db')
    location_target = os.path.join(corpora_root, database_file + '.db')
    
    script_file_create = readscript('create.sql')
#    script_file_clean = readscript('clean.sql')
#    script_file_sample_data = readscript('init_%s.sql' % database_file)
    
    print("Converting document from XML into SQLite3 database")
    print("Database path     : %s" % location_target)
    print("Temp database path: %s" % location)
    
    try:
        conn = sqlite3.connect(location)
        cur = conn.cursor()
        
#        print("Cleaning database ...")
#        timer.start()
#        cur.executescript(script_file_clean)
#        timer.end().report()
#        print("Done!")
        
        print("Creating database ...")
        timer.start()
        cur.executescript(script_file_create)
        timer.end().report()
        print("Database has been created")
        
#        print("Creating sample data ...")
#        timer.start()
#        cur.executescript(script_file_sample_data)
#        timer.end().report()
#        print("sample data have been created")
    except sqlite3.Error as e:
        print('Error: %s', e)
        pass
    finally:
        if conn:
            conn.close()
    
    backup_database(location_target)
        
    print("Renaming file %s --> %s ..." % (location, location_target))
    # shutil.copyfile(location, location_target)   
    os.rename(location, location_target)
    print("--")

class ParseContext:
    def __init__(self, corpora_root='', corpus_name='', doc_name='', dbname='', textDAO=None, sqliteDAO=None, context=None, auto_flush=False, verbose=False, iszip=False):
        if textDAO:
            self.textDAO = textDAO
        else:
            self.textDAO = DocumentDAO.getDAO(DocumentDAO.XML, { 'root': corpora_root, 'corpus': corpus_name, 'document': doc_name})
        if sqliteDAO:
            self.sqliteDAO = sqliteDAO
        else:
            self.sqliteDAO = DocumentDAO.getDAO(DocumentDAO.SQLITE3, {'root': corpora_root, 'dbname' : dbname, 'corpus': corpus_name, 'document': doc_name})
        self.corpus_name = corpus_name
        self.doc_name =doc_name
        self.dbname = dbname
        self.context=context
        self.auto_flush=auto_flush
        self.verbose=verbose
        self.iszip = iszip
    
    def set_doc_name(self, doc_name):
        self.doc_name = doc_name
        self.textDAO.config['document'] = doc_name
        self.sqliteDAO.config['document'] = doc_name
    
    def get_context(self):
        if self.context is None:
            self.context = self.sqliteDAO.buildContext()
        return self.context
    
    def flush(self):
        if self.context is not None:
            self.context.flush()

def convert_with_context(parse_context):
    # analysis
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = open(os.path.join(vkconfig.PROJECT_ROOT, 'logs/action_log_%s_%s.csv' % (parse_context.corpus_name, ts)), 'w')
    log = csv.writer(log_file, lineterminator='\n', delimiter=',', escapechar='\\', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Retrieve corpus information first
    corpus = parse_context.sqliteDAO.getCorpus(parse_context.corpus_name)
    if not corpus:
        print("Corpus doesn't exist. Attempting to create one")
        parse_context.sqliteDAO.createCorpus(corpus_name=parse_context.corpus_name, context=parse_context.context)
        
        if not corpus.ID:
            print(corpus)
            print("Tried to create corpus but failed ... Setup tool will terminate now.")
            return
    elif len(corpus) > 1:
        print("Multiple corpora exist. Script will stop now. Please double check the database consistency.")
        return
    else:
        corpus=corpus[0]
    
    # Now make sure the document exists
    docs = parse_context.sqliteDAO.getDocumentByName(doc_name = parse_context.doc_name)
    if len(docs) > 1:
        print("Multiple docs [name=%s] was found" % parse_context.doc_name)
        print("Error! Script will be terminated.")
        return False
    elif len(docs) == 1:
        print("Document exists. Document will NOT be saved to database.")
        return False
    elif len(docs) == 0:
        print("Doc %s cannot be found. Attempting to create the document ..." % parse_context.doc_name)
        document = Document(parse_context.doc_name, corpus.ID)
        parse_context.sqliteDAO.saveDocument(document, context=parse_context.context)
        #parse_context.flush()
        #docs = parse_context.sqliteDAO.getDocumentByName(doc_name = parse_context.doc_name)
        if not document.ID:
        #if len(docs) != 1:
            print("Tried to create document but failed. Script will be terminated now.")
            return False

    if parse_context.iszip:
        sentenceIDs = parse_context.textDAO.getAllSentences(parse_context.doc_name)
    else:
        sentenceIDs = parse_context.textDAO.getAllSentences()
    print("Found %s sentences" % len(sentenceIDs))
    for id in sentenceIDs:
        if parse_context.verbose:
            print("-> Retrieving sentence %s from text-based document ..." % (id,))
        timer.start()
        sentence = parse_context.textDAO.getSentence(id)
        
        sentence.documentID = document.ID
        if parse_context.verbose: timer.end().report()
        log.writerow([timer.runtime(), "R", id])

        timer.start()
        if parse_context.verbose: print("saving sentence %s to SQLite DB ..." % (id,))
        parse_context.sqliteDAO.saveSentence(sentence,context=parse_context.get_context(),auto_flush=False)
        if parse_context.verbose: timer.end().report()
        log.writerow([timer.runtime(), "W", id])
        if parse_context.verbose: print('')
    print("FINISHED IMPORTING DOC")
    if parse_context.auto_flush:
        if parse_context.verbose: print("... Flushing doc ...")
        parse_context.flush()
    
    # print("DONE! Please see log file for more details")
    log_file.close()

'''
Convert text format into SQLite format
'''
def convert(collection_name, corpus_name, doc_name, dbname=None, context=None, auto_flush=True):
    # analysis
    log_file = open(os.path.join(vkconfig.PROJECT_ROOT, 'logs/action_log.csv'), 'w')
    log = csv.writer(log_file, lineterminator='\n', delimiter=',', escapechar='\\', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # text-based sentence
    # Get a sentence by ID
    bib = Biblioteca(collection_name)
    textDAO = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc_name)
    sqliteDAO = bib.sqldao

    # Retrieve corpus information first
    print("Retrieving corpus ...")
    corpus = sqliteDAO.getCorpus(corpus_name)
    if not corpus:
        print("Corpus doesn't exist. Attempting to create one")
        sqliteDAO.createCorpus(corpus_name=corpus_name)
        corpus = sqliteDAO.getCorpus(corpus_name)
        if not corpus:
            print(corpus)
            print("Tried to create corpus but failed ... Setup tool will terminate now.")
            return
    elif len(corpus) > 1:
        print("Multiple corpora exist. Script will stop now. Please double check the database consistency.")
        return
    
    # Now make sure the document exists
    docs = sqliteDAO.getDocumentByName(doc_name = doc_name)
    if len(docs) > 1:
        print("Multiple docs [name=%s] was found" % doc_name)
        print("Error! Script will be terminated.")
        return False
    elif len(docs) == 1:
        print("Document exists. Document will NOT be saved to database.")
        return False
    elif len(docs) == 0:
        print("Doc %s cannot be found. Attempting to create the document ..." % doc_name)
        sqliteDAO.saveDocument(Document(doc_name, corpus[0].ID))
        docs = sqliteDAO.getDocumentByName(doc_name = doc_name)
        if len(docs) != 1:
            print("Tried to create document but failed. Script will be terminated now.")
            return False

    sentenceIDs = textDAO.getSentences()
    if context == None:
        context = sqliteDAO.buildContext()
    for id in sentenceIDs:
        print("-> Retrieving sentence %s from text-based document ..." % id)
        timer.start()
        sentence = textDAO.getSentence(id)
        
        sentence.documentID = docs[0].ID
        timer.end().report()
        log.writerow([timer.runtime(), "R", id])

        timer.start()
        print("saving sentence %s to SQLite DB ..." % id)
        sqliteDAO.saveSentence(sentence,context=context,auto_flush=False)
        timer.end().report()
        log.writerow([timer.runtime(), "W", id])
        print('')
    print("FINISHED IMPORTING DOC, FLUSHING")
    if auto_flush:
        context.flush()
    
    print("DONE! Please see log file for more details")
    log_file.close()
    return context
    
def main():
    prepare_database(vkconfig.BIBLIOTECHE_ROOT, "test")
    convert('test', "wn", "wndef")
    pass

if __name__ == '__main__':
    # Do NOT use this, use setup.py instead
    main()
    pass
