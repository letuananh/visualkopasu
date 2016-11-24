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

from visualkopasu.config import ViskoConfig as vkconfig
from .simple_parser import parse_document
from .text_to_sqlite import prepare_database
from .text_to_sqlite import convert

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

if sys.version_info >= (3, 0):
    def confirm(msg='Do you want to proceed (yes/no)? '):
        return input(msg).lower() in ['y', 'yes', 'ok']
else:
    def confirm(msg='Do you want to proceed (yes/no)? '):
        return raw_input(msg).lower() in ['y', 'yes', 'ok']


def draw_separator():
    print("-" * 80)


def get_raw_doc_folder(collection_name, corpus_name, doc_name):
    return os.path.join(vkconfig.DATA_FOLDER, "raw", collection_name, corpus_name, doc_name)


def convert_document(collection_name, corpus_name, doc_name, answer=None, active_only=False, ignore_raw=False):
    source_folder = get_raw_doc_folder(collection_name, corpus_name, doc_name)
    dest_folder = os.path.join(vkconfig.BIBLIOTECHE_ROOT, collection_name)
    print("Attempting to parse document from raw text into XML")
    print("Source folder: %s" % source_folder)
    print("Destination folder: %s" % dest_folder)
    print("Biblioteca: %s" % collection_name)
    print("Corpus name: %s" % corpus_name)
    print("Document name: %s" % doc_name)
    # Convert raw text to XML
    if not ignore_raw:
        draw_separator()
        parse_document(source_folder, dest_folder, corpus_name, doc_name, active_only=active_only)
    # Convert XML to SQLite3
    draw_separator()
    db_path = os.path.join(vkconfig.BIBLIOTECHE_ROOT, collection_name + '.db')
    if os.path.exists(db_path):
        print("Now, I'm going to alter the content of the database: %s" % db_path)
        if not (answer or confirm("Do you want to continue? (yes/no): ")):
            return False
    else:
        prepare_database(vkconfig.BIBLIOTECHE_ROOT, collection_name)
    convert(collection_name, corpus_name, doc_name)
    print("All Done!")
    draw_separator()
    return answer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data import tool")

    parser.add_argument('biblioteca', help='Biblioteca name')
    parser.add_argument('corpus', help='Corpus name')
    parser.add_argument('doc', help='Document name')
    parser.add_argument('-a', '--active', help='Only import active interpretations', action='store_true')
    parser.add_argument('-i', '--noraw', help='Import from XML to SQLite only', action='store_true')
    parser.add_argument('-y', '--yes', help='Say yes to everything', action='store_true')
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        if args.biblioteca and args.corpus and args.doc:
            answer = convert_document(args.biblioteca, args.corpus, args.doc, answer=args.yes, active_only=args.active, ignore_raw=(args.noraw))
        else:
            parser.print_help()
    pass
