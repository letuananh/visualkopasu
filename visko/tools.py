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

from visko.config import ViskoConfig as vkconfig
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Visko toolbox")

    parser.add_argument('biblioteca', help='Biblioteca name')
    parser.add_argument('corpus', help='Corpus name')
    parser.add_argument('doc', help='Document name')
    parser.add_argument('-a', '--active', help='Only import active interpretations', action='store_true')
    parser.add_argument('-R', '--raw', help='Import data in FCB format', action='store_true')
    parser.add_argument('-y', '--yes', help='Say yes to everything', action='store_true')
    if len(sys.argv) == 1:
        # User didn't pass any value in, show help
        parser.print_help()
    else:
        # Parse input arguments
        args = parser.parse_args()
        if args.biblioteca and args.corpus and args.doc:
            answer = convert_document(args.biblioteca, args.corpus, args.doc, answer=args.yes, active_only=args.active, use_raw=args.raw)
        else:
            parser.print_help()
    pass
