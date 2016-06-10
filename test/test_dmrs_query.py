'''
Test DMRS query tool
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
__copyright__ = "Copyright 2012, Visual Kopasu"
__credits__ = [ "Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying" ]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import unittest

from visualkopasu.kopasu.dmrs_search import DMRSQueryParser

class TestQueryParser(unittest.TestCase):

    def header(self, a_str):
        print('')
        print("*" * 80)
        print(a_str)
        #print("*" * 80)
        

    def setUp(self):
        pass

    def test_valid_query(self):
        self.header("Test query with space")
        query = "(L:and    NEQ/L-INDEX      bazaar) AND (and /L-INDEX bazaar)AND(      ? / ?)"
        results = DMRSQueryParser.parse(query)
        expected = [['L:and', 'NEQ/L-INDEX', 'bazaar'], ['and', '/L-INDEX', 'bazaar'], ['?', '/', '?']]
        self.assertEqual(expected, results)
        
        self.header("Node query (no bracket)")
        query = "(? / bazaar) AND (? / cathedral) AND (?) AND (and / ?) AND lemma AND G:named_rel"
        results = DMRSQueryParser.parse(query)
        expected = [['?', '/', 'bazaar'], ['?', '/', 'cathedral'], ['?'], ['and', '/', '?'], ['lemma'], ['G:named_rel']]
        self.assertEqual(expected, results)
        
        self.header("a single node query")
        query = "?"
        results = DMRSQueryParser.parse(query)
        expected = [['?']]
        self.assertEqual(expected, results)

        self.header("Node query only (no bracket)")
        query = "AND And and anD And"
        results = DMRSQueryParser.parse(query)
        expected = [['AND'], ['and'], ['And']]
        self.assertEqual(expected, results)

        self.header("Valid query")
        query = "(? / bazaar) AND (? / cathedral) AND (?) AND (and / ?)"
        results = DMRSQueryParser.parse(query)
        expected = [['?', '/', 'bazaar'], ['?', '/', 'cathedral'], ['?'], ['and', '/', '?']]
        self.assertEqual(expected, results)
        
        self.header("Single clause query")
        query = "(? / ?)"
        results = DMRSQueryParser.parse(query)
        expected = [['?', '/', '?']]
        self.assertEqual(expected, results)
        
        self.header("lower-case boolean operator")
        query = '(?) and (?)'
        results = DMRSQueryParser.parse(query)
        expected = [['?'], ['?']]
        self.assertEqual(expected, results)
        
        self.header("Clause with 2 elements")
        query = "(? / ?)AND(? /)"
        results = DMRSQueryParser.parse(query)
        expected = [['?', '/', '?'], ['?', '/']]
        self.assertEqual(expected, results)
        
        self.header("Empty query")
        query = ''
        results = DMRSQueryParser.parse(query)
        expected = []
        self.assertEqual(expected, results)

    def test_invalid_query(self):
        self.header("None query")
        query = None
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Query as an array")
        query = ['a', 'b', 'c', 1]
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Empty clause")
        query = "(? / ?)AND()"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Invalid bracket")
        query = "(? / ?)AND(?"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Invalid bracket (close)")
        query = "(? / ?)AND(?))"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Invalid bracket (open)")
        query = "(? / ?)AND((?)"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Invalid bracket (open) 2 ")
        query = "((?)"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        
        self.header("Multiple boolean operator")
        query = "(?) AND AND (?)"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)
        
        self.header("Invalid clause: 4 elements")
        query = "(? / ?)AND(? / ? ?)"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)

        self.header("Invalid clause: boolean in the end")
        query = "(? / ?)AND(? / ? ?) AND"
        results = DMRSQueryParser.parse(query)
        expected = None
        self.assertEqual(expected, results)

########################################################################

def main():
    unittest.main()

if __name__ == "__main__":
    main()
