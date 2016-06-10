'''
Parse raw text document (ACL dataset) into XML-based format for VisualKopasu
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
__copyright__ = "Copyright 2013, Visual Kopasu"
__credits__ = [ "Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying" ]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

from xml.etree import ElementTree as ETree
from xml.etree.ElementTree import Element, SubElement, Comment

import time, datetime
import os.path
import re
import gzip
from config import VisualKopasuConfiguration as vkconfig
import csv
import logging
import sys
from text_to_sqlite import *
from zipfile import ZipFile
from gzip import GzipFile
import StringIO
from collections import deque

# Init log function
sim_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logger = logging.getLogger('acl_parser')

INTERPRETATION_TOKEN     = chr(10) + chr(12) + chr(10)
DRMS_TREE_TOKEN          = chr(10) + chr(10) + chr(10)
PARSE_TREE_TOKEN         = chr(10) + chr(10)    
DEBUG_MODE               = False

def header(text, style='H2', additional_text=''):
    if style == 'H1':
        print("###################################################")
        print("# " + text)
        print("###################################################")
    else:
        print('')
        print("{{{{{{{{{{---" + text + "---}}}}}}}}}}")
        print('')
    print(additional_text)
    
class ParseConfig:
    def __init__(self, data_root, database_name=None):
        self.data_root = data_root
        self.sentence_list_folder = os.path.join(data_root, 'sentence_list')
        self.database_name = database_name
        self.dmrs_folder = os.path.join(data_root, 'dmrs')
        self.output_folder = os.path.join(data_root, 'output')
        self.logfolder = os.path.join(data_root, 'logs')

class ParserHelper:
    @staticmethod
    def list_files(source_folder):
        all_files = [ f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f)) ]
        return all_files

    @staticmethod
    def list_dirs(source_folder):
        all_files = [ f for f in os.listdir(source_folder) if os.path.isdir(os.path.join(source_folder, f)) ]
        return all_files
    
    @staticmethod
    def makedirs(destination_folder):
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

def parse(dmrs_content_file, sentence_id, sentence_text, destination):
    logger.debug("parsing [{src}] >> ...".format(src=dmrs_content_file))
    
    dmrs_content = open(dmrs_content_file, 'rb').read().decode('utf-8')
        
    # store to XML
    a_sentence = Element('sentence')
    a_sentence.set('version', '1.0')
    
    a_sentence.attrib['id'] = sentence_id.decode('utf-8')
    xml_text_elem = SubElement(a_sentence, 'text')
    xml_text_elem.text = sentence_text.decode('utf-8')
    
    a_interpretation = SubElement(a_sentence, 'interpretation')
    a_interpretation.attrib['id'] = '1'
    a_interpretation.attrib['mode'] = 'active'
    
    try:
        dmrs_node = ETree.fromstring(dmrs_content.encode('utf-8'))
    except Exception, e:
        logger.error("Invalid DMRS XML: %s" % (dmrs_content_file))
        logger.error("Exception: %s" % (e))
        return False
    a_interpretation.append(dmrs_node)

    with gzip.open(destination, 'wb') as output_file:
        # output_file.write(XMLFormatter.format(a_sentence))
        xml_content = ETree.tostring(a_sentence, encoding='UTF-8', method="xml")
        logger.debug("Writing XML content to file...")
        output_file.write(xml_content)
    
    logger.debug("Finished: [{src}] => [{dest}]".format(src=dmrs_content_file, dest=destination))
    
    return True

def parse_doc(config, corpus_name, doc_name, doc_progress=''):
    document_path = os.path.join(config.sentence_list_folder, corpus_name, doc_name, doc_name + "-leg-sentences.txt")
    destination_folder = os.path.join(config.output_folder, corpus_name, doc_name)

    # make output dir if needed
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    total_time = 0
    processed_files = 0
    
    sentences = open(document_path, 'rb').readlines()
    sentences_count = len(sentences)
    for i in range(sentences_count):
        sentence = sentences[i]
        print("Processing sentence corpus=%s - doc=%s (%s) - %s/%s" % (corpus_name, doc_name, doc_progress, i, sentences_count))
        # for each sentence
        pieces = sentence.split('\t')
        if len(pieces) != 5:
            #print("ERROR")
            logger.error("Invalid sentence information: [corpus=%s - docname=%s]%s" % (corpus_name, doc_name, sentence))
        else:
            # 0 - sentenceID, 4 sentence_text
            # A00-1001-s0-combined-dmrs.xml
            dmrs_content_file = os.path.join(config.dmrs_folder, corpus_name, doc_name, '%s-s%s-combined-dmrs.xml' % (doc_name, pieces[0]))
            if not os.path.isfile(dmrs_content_file):
                # header("ERROR, DMRS content cannot be found: %s" % dmrs_content_file)
                logger.error("DMRS content is missing: [corpus=%s - docname=%s] %s" % (corpus_name, doc_name, dmrs_content_file))
                continue
            temp_output_file = os.path.join(destination_folder, "%s-s%s.xml.gz" % (doc_name, pieces[0]))
            destination = os.path.join(destination_folder, "%s-%s.xml.gz" % (doc_name, pieces[0]))
            if not os.path.isfile(destination):
                before_time = time.time()
                # parse the sentence
                results = parse(sentence_text=pieces[4].replace('\r', '').replace('\n', ''), sentence_id=pieces[0], dmrs_content_file=dmrs_content_file, destination=temp_output_file)
                
                after_time = time.time()
                spent_time = after_time - before_time
                logger.debug("Consumed time = %5.2f secs" % spent_time)
                # logger.debug('')
                total_time += spent_time
                processed_files += 1
                
                if results:
                    os.rename(temp_output_file, destination)
            else:
                logger.debug(destination + " is found!")
    logger.debug("Total consumed time = %5.2f secs" % total_time)
        
    pass

def parse_corpora(config):
    #print("Listing %s" % config.sentence_list_folder)
    corpora = ParserHelper.list_dirs(config.sentence_list_folder)
    for corpus in corpora:
        parse_corpus(config, corpus)

def parse_corpus(config, corpus):
    header(corpus)
    documents = ParserHelper.list_dirs(os.path.join(config.sentence_list_folder, corpus))
    doc_count = len(documents)
    for i in range(doc_count):
        doc = documents[i]
        print("Processing doc %s of corpus %s (%s/%s)" % (doc, corpus, i, doc_count))
        parse_doc(config, corpus, doc, doc_progress="%s/%s" % (i, doc_count))       
        # convert(config.output_folder, corpus, doc, dbname=config.database_name)   

def import_corpus(config, corpus):
    documents = ParserHelper.list_dirs(os.path.join(config.sentence_list_folder, corpus))
    doc_count = len(documents)
    
    context = ParseContext(config.output_folder, corpus, '', dbname=config.database_name, auto_flush=False)
    for i in range(doc_count):
        doc = documents[i]
        context.set_doc_name(doc)
        import_doc(config, corpus, doc, '%s/%s' % (i, doc_count), context)
    print("Finished import documents from corpus %s. Flushing corpus to database ..." % corpus)
    context.flush()
    print("DONE!!!")
        
def import_doc(config, corpus, doc, doc_progress, parse_context):
    print("Importing doc %s of corpus %s (%s) into SQLITE DB" % (doc, corpus, doc_progress))
    convert_with_context(parse_context)

class CorpusInfo:
    def __init__(self, root, name):
        self.root = root
        self.name = name

    def get_path(self):
        return os.path.join(self.root, self.name)
        
    def get_documents(self):
        doc_names = ParserHelper.list_dirs(self.get_path())
        docs = []
        for doc_name in doc_names:
            docs.append(DocumentInfo(doc_name, self))
        return docs
    
    def __str__(self):
        return "[Corpus: %s]" % self.get_path()
    
class DocumentInfo:
    def __init__(self, name, corpus):
        self.name = name
        self.corpus = corpus
        
    def get_path(self):
        return os.path.join(self.corpus.get_path(), self.name)
        
    def get_sentences(self):
        sentence_names = ParserHelper.list_files(self.get_path())
        sentences = []
        for sentence_name in sentence_names:
            sentences.append(SentenceInfo(sentence_name, self))
        return sentences
        
    def __str__(self):
        return "[Document: %s]" % self.get_path()           

class SentenceInfo:
    def __init__(self, name, document):
        self.name = name
        self.document = document

    def get_path(self):
        return os.path.join(self.document.get_path(), self.name)

    def __str__(self):
        return "[Sentence: %s]" % self.get_path()       
        
def pack_corpora(config):
    corpora = ParserHelper.list_dirs(os.path.join(config.output_folder))
    
    documents = []
    for corpus_name in corpora:
        corpus = CorpusInfo(config.output_folder, corpus_name)
        print("Found a corpus at: %s ... listing corpus" % corpus)
        documents += corpus.get_documents()
        '''
        print("Listing sentences of the first document %s" % documents[0])
        sentences = documents[0].get_sentences()
        print("The first sentence of that document is: %s" % sentences[0])
        myzip.write(sentences[0].get_path(), sentences[0].get_path().replace(documents[0].get_path(), ''))
        '''
    print("Found %s documents" % len(documents))
    doc_queue = deque(documents)

    groups = []
    while len(doc_queue) > 0:
        group = []
        for i in range(290):
            if(len(doc_queue) >0):
                group.append(doc_queue.popleft())
        groups.append(group)
    
    id = 1
    for group in groups:
        print("Packing ACL_pack%d: %d documents" % (id, len(group)))
        package_path = os.path.join(config.data_root, "acl_corpora", "corpora_acl%d.zip" % id)
        
        with ZipFile(package_path, 'w') as acl_package:
            count = 0
            for document in group:
                count+=1
                print("Package %d - doc %d/%d" % (id, count, len(group)))
                sentences = document.get_sentences()
                for sentence in sentences:
                    acl_package.write(sentence.get_path(), sentence.get_path().replace(sentence.document.corpus.get_path(), ''))
                    #break # only the first sentence
                #break # only the first document
            #break #only the first group
        id += 1
    '''
    # Sample of read code
    with ZipFile(package_path, 'r') as myzip:
    names = myzip.namelist()
    for name in names:
        print(name)
        zipfile = StringIO.StringIO(myzip.read(name))
        content = GzipFile(fileobj=zipfile, mode='rb').readlines()[0]
        print(content)
    '''
    
def list_zipped_corpus(config, package_path):
    if not os.path.isfile(package_path):
        package_path = os.path.join(config.data_root, package_path)
    doc = DocumentDAO.getDAO(DocumentDAO.XML, {'root': '', 'corpus': package_path, 'dbname': package_path})
    '''
    with ZipFile(package_path, 'r') as package_file:
        names = package_file.namelist()
        doc_list = []
        for name in names:
            print(name)
            doc_name = name.split("/")[0]
            if doc_name not in doc_list:
                doc_list.append(doc_name)
                #print(doc_name)
        print("Total doc found: %d" % len(doc_list))
    '''
    documents = doc.getAllDocuments()
    for document in documents:
        sentences = doc.getAllSentences(document)
        print("Document: %s - %s sentences" % (document, len(sentences)))
    print("Total: %s documents" % len(documents))
    
def read_zipped_sentence(config, package_path, document_name, sentence_name):
    if not os.path.isfile(package_path):
        package_path = os.path.join(config.data_root, package_path)
    doc = DocumentDAO.getDAO(DocumentDAO.XML, {'root': '', 'corpus': package_path, 'dbname': package_path})
    content = doc.getSentenceRaw(sentence_name, document_name)
    print(content)
    '''
    if not os.path.isfile(package_path):
        package_path = os.path.join(config.data_root, package_path)
    with ZipFile(package_path, 'r') as package_file:
        sentence_path = document_name + "/" + sentence_name
        content = GzipFile(fileobj=StringIO.StringIO(package_file.read(sentence_path)), mode='rb').read()
        print(content)
    '''

def import_zipped_corpus(config, package_path):
    corpus = package_path[:-4]
    if not os.path.isfile(package_path):
        package_path = os.path.join(config.data_root, package_path)
    
    doc = DocumentDAO.getDAO(DocumentDAO.XML, {'root': '', 'corpus': package_path, 'dbname': package_path})
    documents = doc.getAllDocuments()
    doc_count = len(documents)
    
    context = ParseContext(config.output_folder, corpus, '', dbname=config.database_name, textDAO=doc, auto_flush=False, iszip=True)
    for i in range(doc_count):
        doc = documents[i]
        context.set_doc_name(doc)
        import_zipped_doc(config, corpus, doc, '%s/%s' % (i, doc_count), context)
    print("Finished import documents from corpus %s. Flushing corpus to database ..." % corpus)
    context.flush()
    print("DONE!!!")
        
def import_zipped_doc(config, corpus, doc, doc_progress, parse_context):
    print("Importing doc %s of corpus %s (%s) into SQLITE DB" % (doc, corpus, doc_progress))
    convert_with_context(parse_context)
    
def prompt_usage():
    print(
"""ACL Parser script
Usage:
    General:
        + Create database
        python acl.py --create-db [dbname]
        + Create a new database then import the specified corpus
        --build-corpus-db corpus_name db_name
        + Build corpus from zip file
        --build-zip-corpus-db corpus_name db_name
    
    Packing:
        + Pack a corpus into archive file
        python acl.py --pack-corpora
        + List a zipped corpus
        python acl.py --list-zipped-corpus path/to/zip_file
        + Read a sentence in zipped corpus
        python acl.py --read-zipped-sentence path/to/zip_file doc_name sentence_name
    
    Importing:
        + Import corpus
        python acl.py --import-corpus corpus_name [dbname]
        + Import doc
        python acl.py --import-doc corpus_name doc_name
        
    Parsing:
        + Parse the whole ACL corpora
        python acl.py --parse-corpora
        + Parse 1 raw corpus
        python acl.py --parse-corpus corpus_name
        + Parse 1 doc
        python acl.py --parse-doc corpus_name doc_name
""")
    
def main():
    config = ParseConfig(data_root=vkconfig.ACL_CORPORA_ROOT)
    config.database_name = 'aclT' #vkconfig.ACL_DB_NAME
    
    # makedirs
    ParserHelper.makedirs(config.logfolder)
    
    # log to file
    logfilename = 'acl_parser_%s.txt' % sim_timestamp
    fhdlr = logging.FileHandler(os.path.join(config.logfolder, logfilename))
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
    fhdlr.setFormatter(formatter)
    logger.addHandler(fhdlr) 
    logger.setLevel(logging.ERROR)
    
    if len(sys.argv) == 1:
        prompt_usage()
    else:
        if sys.argv[1] == '--create-db':
            if len(sys.argv) < 1:
                prompt_usage()
            else:
                config.database_name = sys.argv[2]
                prepare_database(config.output_folder, config.database_name)
        elif sys.argv[1] == '--parse-corpus':
            if len(sys.argv) == 3:
                parse_corpus(config, sys.argv[2])
            else:
                # Parse raw corpus
                prompt_usage()
        elif sys.argv[1] == '--import-corpus':
            if len(sys.argv) == 3:
                import_corpus(config, sys.argv[2])
            elif len(sys.argv) == 4:
                config.database_name = sys.argv[3]
                import_corpus(config, sys.argv[2])
            else:
                prompt_usage()
        elif sys.argv[1] == '--pack-corpora':
            if len(sys.argv) == 2:
                pack_corpora(config)
            else:
                prompt_usage()
        elif sys.argv[1] == '--list-zipped-corpus':
            if len(sys.argv) == 3:
                list_zipped_corpus(config, sys.argv[2])
            else:
                prompt_usage()
        #python acl.py --read-zipped-sentence path/to/zip_file doc_name sentence_name
        elif sys.argv[1] == '--read-zipped-sentence':
            if len(sys.argv) == 5:
                read_zipped_sentence(config, sys.argv[2], sys.argv[3], sys.argv[4])
            else:
                prompt_usage()
        elif sys.argv[1] == '--build-corpus-db':
            if len(sys.argv) == 4:
                config.database_name = sys.argv[3]
                prepare_database(config.output_folder, config.database_name)
                import_corpus(config, sys.argv[2])
            else:
                prompt_usage()
        elif sys.argv[1] == '--build-zip-corpus-db':
            if len(sys.argv) == 4:
                config.output_folder = config.data_root
                config.database_name = sys.argv[3]
                prepare_database(config.output_folder, config.database_name)
                import_zipped_corpus(config, sys.argv[2])
            else:
                prompt_usage()
        elif sys.argv[1] == '--parse-doc':
            if len(sys.argv) == 4:
                parse_doc(config, sys.argv[2], sys.argv[3])
            else:
                prompt_usage()
        elif sys.argv[1] == '--import-doc':
            if len(sys.argv) == 4:
                import_doc(config, sys.argv[2], sys.argv[3])
    header("DONE!")
    
if __name__ == "__main__":
    #main()
    # do not use this, use setup.py instead
    pass
