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
import logging
from visko.kopasu import Biblioteca
from visko.kopasu.dmrs_search import DMRSQueryParser, LiteSearchEngine


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
SEARCH_LIMIT = 10000


class TestDMRSSearch(unittest.TestCase):

    bib = Biblioteca('test')
    engine = LiteSearchEngine(bib.sqldao, limit=SEARCH_LIMIT)

    @classmethod
    def setUpClass(cls):
        print(cls.engine.dao.db_path)

    def test_lower_case(self):
        sents = self.engine.search('linus')
        self.assertTrue(sents)

    def test_build_node_query(self):
        clauses = DMRSQueryParser.parse('G:named_rel')
        nq = DMRSQueryParser.parse_node(clauses[0][0])
        q = nq.to_query()
        self.assertEqual(q.query, ('SELECT DISTINCT dmrsID FROM dmrs_node node WHERE gpred_valueID = (SELECT ID FROM dmrs_node_gpred_value WHERE value = ?)'))
        self.assertEqual(q.params, ['named_rel'])

    def test_build_link_query(self):
        clauses = DMRSQueryParser.parse('(G:compound_rel / hack)')
        c = clauses[0]
        lnk = DMRSQueryParser.parse_link(c[1], c[0], c[2])
        self.assertEqual(lnk.to_query().params, ['compound_rel', 'hack', 'hack'])

    def test_search_lemma_or_carg(self):
        sents = self.engine.search('act')
        self.assertIsNotNone(sents)
        self.assertGreaterEqual(len(sents), 2)

    def test_search_carg(self):
        sents = self.engine.search('C:Linus')
        self.assertGreaterEqual(len(sents), 1)

    def test_search_lemma2(self):
        sents = self.engine.search('L:bazaar')
        self.assertGreaterEqual(len(sents), 1)

    def test_search_pred(self):
        sents = self.engine.search('G:pron')
        self.assertGreater(len(sents), 10)

    def test_search_compound(self):
        sents = self.engine.search('G:pron AND code')
        self.assertGreater(len(sents), 5)

    def test_search_compound2(self):
        cs = DMRSQueryParser.parse('G:named AND bazaar')
        self.assertEqual(cs, [['G:named'], ['bazaar']])
        sents = self.engine.search('G:named AND bazaar')
        self.assertGreaterEqual(len(sents), 1)

    def test_search_link(self):
        sents = self.engine.search('(know /ARG1 ?)')
        self.assertGreaterEqual(len(sents), 0)
        sents = self.engine.search('(want /ARG2 get)')
        self.assertGreaterEqual(len(sents), 0)
        sents = self.engine.search('(want /ARG1 G:pron)')
        self.assertGreaterEqual(len(sents), 0)

    def test_complex_search(self):
        sents = self.engine.search('(want /ARG1 G:pron) AND ready')
        self.assertGreaterEqual(len(sents), 0)

    def test_search_by_sid(self):
        ident = '#1930'
        q = DMRSQueryParser.parse(ident)
        self.assertTrue(q)
        sents = self.engine.search('#1930')
        self.assertTrue(sents)


########################################################################

def main():
    unittest.main()


if __name__ == "__main__":
    main()
