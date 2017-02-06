'''
Test Visual Kopasu
@author: Le Tuan Anh
'''

# Copyright 2016, Le Tuan Anh (tuananh.ke@gmail.com)
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
__copyright__ = "Copyright 2016, Visual Kopasu"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import unittest
from test.test_dmrs_dao import *
from test.test_setup import *
from test.test_dmrs_query import *
from test.test_search import *

from coolisf.model import Sentence

from visualkopasu.config import Biblioteca
from visualkopasu.kopasu.util import RawXML

########################################################################


class TestMain(unittest.TestCase):

    testbib = Biblioteca('test')
    corpus_name = 'minicb'
    doc_name = 'cb100'

    def test_process_raw(self):
        cbdao = self.testbib.textdao.getCorpusDAO(self.corpus_name).getDocumentDAO(self.doc_name)
        sentences = cbdao.getSentences()
        self.assertEqual(len(sentences), 100)
        raw = RawXML(cbdao.getSentenceRaw(sentences[0]))
        self.assertIsNotNone(raw)
        self.assertEqual(len(raw), 1)
        self.assertEqual(raw.text, 'The Cathedral and the Bazaar')
        # rebuild ISF sentence from this?
        sent_isf = Sentence(raw.text)
        sent_isf.add_from_xml(raw.parses[0].dmrs_str())
        print(sent_isf.mrses[0].mrs_json())
        print(sent_isf.mrses[0].dmrs_json())

def main():
    unittest.main()

if __name__ == "__main__":
    main()
