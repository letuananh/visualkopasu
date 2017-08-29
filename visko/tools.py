#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Database setup script for VisualKopasu
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

import sys
import os
import argparse
from lxml import etree

from chirptext import confirm
from visko.config import ViskoConfig as vkconfig
from visko.kopasu.bibman import Biblioteca
from visko.merchant.redwood import parse_document
from visko.merchant.morph import xml2db

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

def get_raw_doc_folder(collection_name, corpus_name, doc_name):
    return os.path.join(vkconfig.DATA_FOLDER, "raw", collection_name, corpus_name, doc_name)


def convert_document(collection_name, corpus_name, doc_name, answer=None, active_only=False, use_raw=False):
    ''' Convert XML to DB '''
    raw_folder = get_raw_doc_folder(collection_name, corpus_name, doc_name)
    collection_folder = os.path.join(vkconfig.BIBLIOTECHE_ROOT, collection_name)
    print("Attempting to parse document from raw text into XML")
    print("Source folder: %s" % raw_folder)
    print("Collection folder: %s" % collection_folder)
    print("Biblioteca: %s" % collection_name)
    print("Corpus name: %s" % corpus_name)
    print("Document name: %s" % doc_name)
    # Convert XML to SQLite3
    if use_raw:
        parse_document(raw_folder, collection_folder, corpus_name, doc_name)
    # create a bib
    xml2db(collection_name, corpus_name, doc_name)
    print("All Done!")
    return answer


def import_xml(args):
    answer = convert_document(args.biblioteca, args.corpus, args.doc, answer=args.yes, active_only=args.active, use_raw=args.raw)
    return answer


def export_sqlite(args):
    bib = Biblioteca(args.biblioteca, root=args.root)
    dao = bib.sqldao
    corpus = dao.getCorpus(args.corpus)
    doc = dao.get_doc(args.doc)
    if os.path.exists(args.filename):
        print("Output path exists. Cannot export data")
        return False
    elif corpus is None or doc is None or corpus.ID != doc.corpusID:
        print("Document does not exist ({}/{}/{} was provided)".format(args.biblioteca, args.corpus, args.doc))
    else:
        # found doc
        sents = dao.getSentences(doc.ID)
        doc_node = etree.Element("document")
        doc_node.set("id", str(doc.ID))
        doc_node.set("name", doc.name)
        if doc.title:
            doc_node.set("title", doc.title)
        print("Reading sentences from SQLite")
        for sentinfo in sents:
            sent = dao.getSentence(sentinfo.ID)
            sent_node = sent.to_isf().to_visko_xml()
            doc_node.append(sent_node)
        print("Saving sentences to {}".format(args.filename))
        with open(args.filename, 'wb') as outfile:
            outfile.write(etree.tostring(doc_node, pretty_print=True, encoding="utf-8"))
        print("Done")


def store_report(args):
    bib = Biblioteca(args.biblioteca, root=args.root)
    dao = bib.sqldao
    corpus = dao.getCorpus(args.corpus)
    doc = dao.get_doc(args.doc)
    report_loc = bib.textdao.getCorpusDAO(args.corpus).getDocumentDAO(args.doc).path + ".report.xml"
    if not os.path.exists(report_loc):
        print("There is no report to import.")
        return False
    elif corpus is None or doc is None or corpus.ID != doc.corpusID:
        print("Document does not exist ({}/{}/{} was provided)".format(args.biblioteca, args.corpus, args.doc))
        return False
    else:
        with dao.ctx() as ctx:
            # read doc sents
            sents = dao.getSentences(doc.ID, ctx=ctx)
            sent_map = {s.ident: s for s in sents}
            # read comments
            tree = etree.iterparse(report_loc)
            for event, element in tree:
                if event == 'end' and element.tag == 'sent':
                    id = element.get('ID')
                    ident = element.get('ident')
                    # flag = element.get('flag')
                    # text = element.find('text').text
                    comment = element.find('comment').text
                    # import comment here
                    # Only import comments to sentences with empty comment
                    if comment and ident in sent_map and not sent_map[ident].comment:
                        sent = sent_map[ident]
                        print("comment to #{} ({}): {}".format(id, ident, comment))
                        dao.note_sentence(sent.ID, comment.strip(), ctx=ctx)
                    element.clear()


def gen_report(args):
    bib = Biblioteca(args.biblioteca, root=args.root)
    dao = bib.sqldao
    corpus = dao.getCorpus(args.corpus)
    doc = dao.get_doc(args.doc)
    report_loc = bib.textdao.getCorpusDAO(args.corpus).getDocumentDAO(args.doc).path + ".report.xml"
    if os.path.exists(report_loc) and not confirm("Report file exists. Do you want to continue (Y/N)? "):
        print("Program aborted.")
        return False
    elif corpus is None or doc is None or corpus.ID != doc.corpusID:
        print("Document does not exist ({}/{}/{} was provided)".format(args.biblioteca, args.corpus, args.doc))
    else:
        # found doc
        sents = dao.getSentences(doc.ID)
        doc_node = etree.Element("document")
        doc_node.set("id", str(doc.ID))
        doc_node.set("collection", args.biblioteca)
        doc_node.set("corpus", corpus.name)
        doc_node.set("name", doc.name)
        if doc.title:
            doc_node.set("title", doc.title)
        # save comments
        for sent in sents:
            if args.concise and not (sent.comment or sent.flag):
                continue
            sent_node = etree.SubElement(doc_node, 'sent')
            sent_node.set('ID', str(sent.ID))
            sent_node.set('ident', str(sent.ident))
            if sent.flag:
                sent_node.set('flag', str(sent.flag))
            text_node = etree.SubElement(sent_node, 'text')
            text_node.text = sent.text
            comment_node = etree.SubElement(sent_node, 'comment')
            cmt = '\n\t\t{}\n'.format(sent.comment.replace('\n', '\n\t\t')) if sent.comment else ''
            comment_node.text = etree.CDATA(cmt)
        print("Saving sentences to {}".format(report_loc))
        with open(report_loc, 'wb') as outfile:
            outfile.write(etree.tostring(doc_node, pretty_print=True, encoding="utf-8"))
        print("Done")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Visko toolbox")

    tasks = parser.add_subparsers(help='Task to be done')

    # import XML => SQLite
    import_task = tasks.add_parser("import", help="Import sentences in XML format")
    import_task.add_argument('biblioteca', help='Biblioteca name')
    import_task.add_argument('corpus', help='Corpus name')
    import_task.add_argument('doc', help='Document name')
    import_task.add_argument('-f', '--file', help='XML file (a big XML file instead of many small XML files)')
    import_task.add_argument('-a', '--active', help='Only import active readings', action='store_true')
    import_task.add_argument('-R', '--raw', help='Import data in FCB format', action='store_true')
    import_task.add_argument('-y', '--yes', help='Say yes to everything', action='store_true')
    import_task.set_defaults(func=import_xml)

    # export SQLite => XML
    export_task = tasks.add_parser("export", help="Export SQLite to XML")
    export_task.add_argument('biblioteca', help='Biblioteca name')
    export_task.add_argument('corpus', help='Corpus name')
    export_task.add_argument('doc', help='Document name')
    export_task.add_argument('filename', help='Backup filename')
    export_task.add_argument('--root', help="Biblioteche root", default=vkconfig.BIBLIOTECHE_ROOT)
    export_task.set_defaults(func=export_sqlite)

    # generate report (using comments)
    report_task = tasks.add_parser("report", help="Generate report")
    report_task.add_argument('biblioteca', help='Biblioteca name')
    report_task.add_argument('corpus', help='Corpus name')
    report_task.add_argument('doc', help='Document name')
    report_task.add_argument('--root', help="Biblioteche root", default=vkconfig.BIBLIOTECHE_ROOT)
    report_task.add_argument('--concise', help="Only report commented sentences", default=True, action='store_true')
    report_task.set_defaults(func=gen_report)

    # store report into document
    store_report_task = tasks.add_parser("comment", help="Import comments")
    store_report_task.add_argument('biblioteca', help='Biblioteca name')
    store_report_task.add_argument('corpus', help='Corpus name')
    store_report_task.add_argument('doc', help='Document name')
    store_report_task.add_argument('--root', help="Biblioteche root", default=vkconfig.BIBLIOTECHE_ROOT)
    store_report_task.add_argument('--concise', help="Only report commented sentences", default=True, action='store_true')
    store_report_task.set_defaults(func=store_report)

    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        args.func(args)
