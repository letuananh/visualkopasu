#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data import tool
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

import os
import logging
from texttaglib.chirptext import Timer
from coolisf.model import Document
from visko.kopasu.bibman import Biblioteca

# -------------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# -------------------------------------------------------------------------------
# FUNCTIONS
# -------------------------------------------------------------------------------

def xml2db(collection_name, corpus_name, doc_name, archive_file=None):
    """
    Import an XML document into SQLite DB
    """
    # text-based sentence
    # Get a sentence by ID
    bib = Biblioteca(collection_name)
    textDAO = bib.textdao.getCorpusDAO(corpus_name).getDocumentDAO(doc_name)
    sqliteDAO = bib.sqldao
    timer = Timer()

    # Retrieve corpus information first
    corpus = sqliteDAO.get_corpus(corpus_name)
    if corpus is None:
        sqliteDAO.create_corpus(corpus_name=corpus_name)
        corpus = sqliteDAO.get_corpus(corpus_name)
        if corpus is None:
            print(corpus)
            print("Tried to create corpus {} but failed ... Setup tool will terminate now.".format(corpus_name))
            return False
    # Now make sure the document exists
    doc = sqliteDAO.get_doc(doc_name)
    if doc is not None:
        sents = sqliteDAO.get_sents(doc.ID)
        if len(sents):
            print("Document exists. Document will NOT be saved to database.")
            return False
    else:
        sqliteDAO.save_doc(Document(doc_name, corpus.ID))
        doc = sqliteDAO.get_doc(doc_name)
        if doc is None:
            print("Tried to create document but failed. Script will be terminated now.")
            return False

    with sqliteDAO.ctx() as ctx:
        # if archive is available, import from there
        if archive_file is not None:
            # import from archive_file
            print("Reading document from: {}".format(archive_file))
            ar_doc = Document.from_file(archive_file)
            print("Importing {} sentences into {}/{}/{}".format(len(ar_doc), collection_name, corpus_name, doc_name))
            for sent in ar_doc:
                print("Importing sent #{} into doc #{} ({})".format(sent.ident, doc.ID, doc_name))
                sent.ID = None  # reset sentence ID [TODO] or convert it to int if not None?
                sent.docID = doc.ID
                sqliteDAO.save_sent(sent, ctx=ctx)
            print("Done!")
        elif textDAO.is_archived():
            fsize = os.path.getsize(textDAO.archive_path)
            print("Importing from archive: {} (size={})".format(textDAO.archive_path, fsize))
            for sent in textDAO.iter_archive():
                sent.ID = None
                sent.docID = doc.ID
                timer.start("Importing sentence {} to SQLite DB".format(sent))
                sqliteDAO.save_sent(sent, ctx=ctx)
                timer.end()
        elif len(textDAO.get_sents()):
            sentids = textDAO.get_sents()
            for sentid in sentids:
                # read sentence from XML
                timer.start("-> Importing sentence %s from XML ..." % sentid)
                sentence = textDAO.get_sent(sentid)
                sentence.docID = doc.ID
                timer.end()
                # write sentence to DB
                timer.start()
                sqliteDAO.save_sent(sentence, ctx=ctx)
                timer.end("Sentence {} was saved to SQLite DB (sentID={})...".format(sentid, sentence.ID))
        logger.info("Document has been imported.")
    logger.info("DONE! Please see log file for more details")
