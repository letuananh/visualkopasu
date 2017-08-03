'''
Parse raw text document into XML-based format for VisualKopasu
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

import time
import os.path
import re
import gzip
import logging

from xml.etree import ElementTree as ETree
from xml.etree.ElementTree import Element, SubElement, Comment

from visualkopasu.config import ViskoConfig as vkconfig

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

INTERPRETATION_TOKEN = chr(10) + chr(12) + chr(10)
DRMS_TREE_TOKEN = chr(10) + chr(10) + chr(10)
PARSE_TREE_TOKEN = chr(10) + chr(10)


def stripComment(text):
    return re.split('\n{0,1};;; {0,1}', text)


def parse(source_file, destination, active_only=True):
    logging.info("parsing [{src}] ...".format(src=source_file, dest=destination))
    raw_text = gzip.open(source_file).read().decode('utf-8')
    repres_raw = raw_text.split(INTERPRETATION_TOKEN)
    # store to XML
    a_sentence = Element('sentence')
    a_sentence.set('version', '1.0')
    for part in repres_raw:
        logging.debug("FOUND AN INTERPRETATION", "H1")
        a_interpretation = None
        elems = part.split(DRMS_TREE_TOKEN)
        for elem in elems:
            if(elem.startswith("<dmrs ")):
                if a_interpretation is None:
                    break
                logging.debug('DMRS', 'H2', elem)
                dmrs_node = ETree.fromstring(elem.encode('utf-8'))
                a_interpretation.append(dmrs_node)
            elif elem.startswith("["):
                pieces = elem.split(PARSE_TREE_TOKEN)
                for piece in pieces:
                    if piece.startswith("("):
                        if a_interpretation is None:
                            break
                        logging.debug('Syntactic tree', 'H2', piece)
                        # XXX: To XML
                        syntree_node = SubElement(a_interpretation, 'parsetree')
                        syntree_node.text = piece
                    elif piece.startswith("["):
                        logging.debug('Header', 'H2', piece)
                        if a_interpretation is None:
                            mt = re.match("\[(\d+):(\d+)\]\s\((active|inactive)\)", piece)
                            if active_only and mt.group(3) != 'active':
                                break                           
                            a_interpretation = SubElement(a_sentence, 'interpretation')
                            a_interpretation.attrib['id'] = mt.group(2)
                            a_interpretation.attrib['mode'] = mt.group(3)
            elif elem.startswith(";;;"):
                # this will be a header
                pieces = elem.split(PARSE_TREE_TOKEN)
                for piece in pieces:
                    if piece.startswith(";;;"):
                        cmt = stripComment(piece)
                        logging.debug('Comment', 'H2', '\n'.join(cmt))
                        # Store to sentence
                        comment = Comment("\n".join(cmt))
                        a_sentence.append(comment)
                    elif piece.startswith("["):
                        logging.debug('Sentence info', 'H2', piece)
                        mt = re.match("\[(\d+)\][^`]+`(.*)'", piece)
                        a_sentence.attrib['id'] = mt.group(1)
                        xml_text_elem = SubElement(a_sentence, 'text')
                        xml_text_elem.text = mt.group(2)
            elif elem.startswith('<mrs'):
                pass  # XXX We ignore mrs node for now
            else:
                logging.debug("UNKNOWN elem: >>> ||%s||" % (elem,))

    with gzip.open(destination, 'wb') as output_file:
        # output_file.write(XMLFormatter.format(a_sentence))
        xml_content = ETree.tostring(a_sentence, encoding='UTF-8', method="xml")
        logging.info("Writing XML content to file...")
        output_file.write(xml_content)
    print("Finished: [{src}] => [{dest}]".format(src=source_file, dest=destination))
    return None


def parse_document(source_folder, collection_folder, corpus_name, doc_name, active_only=True):
    ''' Convert FCB (redwood) format to XML format '''
    all_files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    all_files.sort()
    destination_folder = os.path.join(collection_folder, corpus_name, doc_name)
    total_time = 0
    processed_files = 0
    for filename in all_files:
        file_id = filename.split('.')[0]
        source_file = os.path.join(source_folder, str(file_id) + ".gz")
        # make output dir if needed
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        output_file = os.path.join(collection_folder, corpus_name, doc_name, "sentence_" + str(file_id) + ".xml.gz")
        destination = os.path.join(collection_folder, corpus_name, doc_name, str(file_id) + ".xml.gz")
        if not os.path.isfile(destination):
            before_time = time.time()
            parse(source_file, output_file, active_only=active_only)
            after_time = time.time()
            spent_time = after_time - before_time
            print("Consumed time = %5.2f secs\n" % spent_time)
            total_time += spent_time
            processed_files += 1
            os.rename(output_file, destination)
        else:
            logging.debug(destination + " is found!")
    print("Total consumed time = %5.2f secs" % total_time)


def main():
    corpus_name = "redwoods"
    doc_name = "cb"
    source_folder = os.path.join(vkconfig.BIBLIOTECHE_ROOT, "raw", corpus_name, doc_name)
    parse_document(source_folder, vkconfig.BIBLIOTECHE_ROOT, corpus_name, doc_name)


if __name__ == "__main__":
    # main()
    # do not use this, use setup.py instead
    pass
