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

    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        args.func(args)
