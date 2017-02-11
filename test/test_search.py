'''
Test DMRS search
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
from test.test_dmrs_dao import TestDAOBase
from visualkopasu.kopasu import Biblioteche, Biblioteca
# from visualkopasu.kopasu.dmrs_search import DMRSQueryParser
from visualkopasu.kopasu.dmrs_search import LiteSearchEngine


class TestDMRSSearch(TestDAOBase):

    DEFAULT_LIMIT = 10000

    def setUp(self):
        pass

    def test_search_lemma(self):
        bibs = Biblioteche.list_all(self.bibroot)
        self.assertEqual(len(bibs), 1)
        bib = Biblioteca(self.bibroot)
        engine = LiteSearchEngine(bib.sqldao, limit=self.DEFAULT_LIMIT)
        print(engine.dao.db_path)
        sentences = engine.search('act')
        print(sentences)


########################################################################


def main():
    unittest.main()


if __name__ == "__main__":
    main()
