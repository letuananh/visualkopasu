'''
List all document in ACL corpus
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

import os.path
import sys
import time, datetime
import re
import gzip
import csv
import logging

from xml.etree import ElementTree as ETree
from xml.etree.ElementTree import Element, SubElement, Comment

from visualkopasu.config import ViskoConfig as vkconfig
from setup.acl_parser import header, ParseConfig, ParserHelper  

# Init log function
sim_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logger = logging.getLogger('acl_parser')

def main():
    config = ParseConfig(data_root=vkconfig.ACL_CORPORA_ROOT)
    config.database_name = vkconfig.ACL_DB_NAME
    
    # makedirs
    ParserHelper.makedirs(config.logfolder)
    
    # log to file
    logfilename = 'acl_parser_%s.txt' % sim_timestamp
    fhdlr = logging.FileHandler(os.path.join(config.logfolder, logfilename))
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
    fhdlr.setFormatter(formatter)
    logger.addHandler(fhdlr) 
    logger.setLevel(logging.ERROR)
    
    # list corpus
    with open(os.path.join(config.output_folder, "doc_list.txt"), "wb") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        corpora = ParserHelper.list_dirs(config.output_folder)
        for corpus in corpora:
            header("Listing doc in corpus: %s" % corpus)
            documents = ParserHelper.list_dirs(os.path.join(config.dmrs_folder, corpus))
            for document in documents:
                csv_writer.writerow([corpus, document])
                print("-> %s" % document)
            csv_file.flush()

    header("DONE!")
    
    
    

if __name__ == "__main__":
    main()
    pass
