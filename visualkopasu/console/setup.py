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

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2012, Visual Kopasu"
__credits__ = [ "Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying" ]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os, sys
#from config import VisualKopasuConfiguration as vkconfig
from .simple_parser import *
from .text_to_sqlite import *

if sys.version_info >= (3,0):
    def confirm(msg='Do you want to proceed (yes/no)? '):
        return input(msg).lower() in [ 'y', 'yes', 'ok' ]
else:
    def confirm(msg='Do you want to proceed (yes/no)? '):
        return raw_input(msg).lower() in [ 'y', 'yes', 'ok' ]

def draw_separator():
    print("-" * 80)
    
def convert_document(corpus_name, doc_name, prepare_db = False, answer = None, active_only=True):
    if answer is not None and answer != 'yes':
        return
    source_folder = os.path.join(vkconfig.CORPORA_FOLDER, "raw", corpus_name, doc_name)
    print("Attempting to parse document from raw text into XML")
    print("Source folder: %s" % source_folder)
    print("Destination folder: %s" % vkconfig.CORPORA_FOLDER)
    print("Corpus name: %s" % corpus_name)
    print("Document name: %s" % doc_name)
    
    # Convert raw text to XML
    parse_document(source_folder, vkconfig.CORPORA_FOLDER, corpus_name, doc_name, active_only=active_only)
    draw_separator()
    
    # Convert XML to SQLite3
    print("Now, I'm going to alter the content of the database: %s" % os.path.join(vkconfig.CORPORA_FOLDER, corpus_name + '.db'))
    if answer or confirm("Do you want to continue? (yes/no): "):
        if prepare_db:
            prepare_database(vkconfig.CORPORA_FOLDER, corpus_name)
        else:
            print("I will add the document to the current database. Existing documents will be kept.")
        convert(vkconfig.CORPORA_FOLDER, corpus_name, doc_name)
    #----------------DONE----------
    print("All Done!")
    draw_separator()
    return answer
    
if __name__ == '__main__':
    # sys.setdefaultencoding('utf-8')
    # print(sys.getdefaultencoding())
    corpus_name = "redwoods"
    doc_name = "cb"
    active_only = False
    
    answer = convert_document(corpus_name, "cb", True, active_only=active_only)
    #convert_document(corpus_name, "sc01", False, answer, active_only=active_only)
    #convert_document(corpus_name, "sc02", False, answer, active_only=active_only)
    #convert_document(corpus_name, "sc03", False, answer, active_only=active_only)
    
    pass
