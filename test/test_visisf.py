#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test Visko-ISF integration
Latest version can be found at https://github.com/letuananh/visualkopasu

References:
    Python documentation:
        https://docs.python.org/
    Python unittest
        https://docs.python.org/3/library/unittest.html
    --
    PEP 257 - Python Docstring Conventions:
        https://www.python.org/dev/peps/pep-0257/

@author: Le Tuan Anh <tuananh.ke@gmail.com>
'''

# Copyright (c) 2017, Le Tuan Anh <tuananh.ke@gmail.com>
#
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

__author__ = "Le Tuan Anh <tuananh.ke@gmail.com>"
__copyright__ = "Copyright 2016, visualkopasu"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "<tuananh.ke@gmail.com>"
__status__ = "Prototype"

########################################################################

import os
import logging
from lxml import etree
import unittest

from chirptext.texttaglib import TagInfo
from coolisf.util import GrammarHub
from coolisf.model import MRS, DMRS
from visko.kopasu.xmldao import getSentenceFromXML, getDMRSFromXML
from visko.kopasu.xmldao import getSentenceFromFile
from visko.kopasu.xmldao import RawXML
from visko.kopasu.util import tokenize_dmrs_str
from visko.kopasu.util import parse_dmrs_str
from visko.kopasu.util import dmrs_str_to_xml
from visko.kopasu.util import str_to_dmrs
from visko.kopasu.util import parse_dmrs
from visko.kopasu.util import xml_to_str


########################################################################

logging.basicConfig(level=logging.WARNING)  # change to DEBUG for more info
TEST_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_FILE = os.path.join(TEST_DIR, '10022.xml.gz')
TEST_FILE2 = os.path.join(TEST_DIR, '10044.xml.gz')

ghub = GrammarHub()
ERG = ghub.ERG


class TestRawXML(unittest.TestCase):

    ghub = GrammarHub()
    ERG = ghub.ERG

    def test_read_from_xml(self):
        raw = RawXML.from_file(TEST_FILE)
        self.assertEqual(raw.text, '"My name is Sherlock Holmes.')
        self.assertEqual(len(raw), 1)
        # should have both MRS and DMRS
        self.assertGreater(len(raw[0].mrs_str()), 0)
        logging.debug(raw[0].mrs.text)
        self.assertGreater(len(raw[0].dmrs_str()), 0)
        logging.debug(raw[0].dmrs_str())

    def test_read_10044(self):
        raw = RawXML.from_file(TEST_FILE2)
        # test RawXML.RawParse > DMRS and MRS
        m = MRS(raw[0].mrs.text)
        self.assertIsNotNone(m.obj())
        self.assertIsNotNone(m.to_dmrs())
        # save 10044 to XML file
        x = raw[0].dmrs_str()
        f = os.path.join(TEST_DIR, 'v10044.xml')
        with open(f, 'w') as outfile:
            outfile.write(x)
        # read it back
        print("Reading from {}".format(f))
        with open(f, 'r') as infile:
            x = infile.read()
            print(len(x))
            d = DMRS(x)
            self.assertIsNotNone(d.obj())
        # seems OK


class TestMain(unittest.TestCase):

    def test_txt2isf(self):
        txt = 'Three musketeers and a giant walk into a bar.'
        # create a Grammar to parse text
        isent = ghub.parse(txt, 'ERG', 10, TagInfo.LELESK)
        self.assertEqual(len(isent), 10)
        # convert ISF sentence into an XML node
        xsent = isent.to_visko_xml()
        self.assertTrue(isinstance(xsent, etree._Element))
        # xsent to visko
        vsent = getSentenceFromXML(xsent)
        self.assertEqual(vsent.text, txt)
        self.assertEqual(len(vsent), 10)
        self.assertEqual(len(vsent.readings[0].raws), 2)

    def test_mfs_2_visko(self):
        txt = 'Three musketeers and a giant walk into a bar.'
        # create a Grammar to parse text
        isent = ghub.parse(txt, 'ERG', 10, TagInfo.MFS)
        xsent = isent.tag_xml().to_visko_xml()
        vsent = getSentenceFromXML(xsent)
        print(vsent[0].dmrs[0])

    def test_visko2isf(self):
        isent = ERG.parse('I saw a girl with a telescope.', parse_count=10)
        vsent = getSentenceFromXML(isent.to_visko_xml())
        # convert back to isf
        isent2 = vsent.to_isf()
        self.assertIsNotNone(isent2)
        self.assertEqual(len(isent), len(isent2))

    def test_str_to_dmrs(self):
        dstr = '''dmrs {
10000 [ generic_entity<0:4> x NUM=sg PERS=3 GEND=n   ] ; 
10001 [ _this_q_dem<0:4>    ] ; 
10002 [ _be_v_id<5:7> e SF=prop TENSE=pres MOOD=indicative PROG=- PERF=- synsetid=02604760-v synset_lemma=be synset_score=0  ] ; 
10003 [ _a_q<8:9>  synsetid=13658027-n synset_lemma=a synset_score=0  ] ; 
10005 [ udef_q<10:18>    ] ; 
10007 [ _cart_n_1<10:19> x NUM=sg PERS=3 IND=+ synsetid=02970849-n synset_lemma=cart synset_score=0  ] ; 
0:/H -> 10002 ; 
10001:RSTR/H -> 10000 ; 
10002:ARG1/NEQ -> 10000 ; 
10002:ARG2/NEQ -> 10007 ; 
10003:RSTR/H -> 10007 ; 
10005:RSTR/H -> 10007 ;
}'''
        dxml = dmrs_str_to_xml(dstr)
        d = getDMRSFromXML(dxml)
        self.assertIsNotNone(d)

    def test_str_with_cargs(self):
        dstr = '''dmrs {
10000 [ def_explicit_q<0:2>    ] ; 
10001 [ poss<0:2> e SF=prop TENSE=untensed MOOD=indicative PROG=- PERF=-   ] ; 
10002 [ pronoun_q<0:2>    ] ; 
10003 [ pron<0:2> x NUM=sg PERS=1   ] ; 
10004 [ _name_n_of<3:7> x NUM=sg PERS=3 IND=+   ] ; 
10005 [ _be_v_id<8:10> e SF=prop TENSE=pres MOOD=indicative PROG=- PERF=-   ] ; 
10006 [ proper_q<11:26>    ] ; 
10007 [ compound<11:26> e SF=prop TENSE=untensed MOOD=indicative PROG=- PERF=-   ] ; 
10008 [ proper_q<11:19>    ] ; 
10009 [ named<11:19> x NUM=sg PERS=3 IND=+  CARG=+ ] ; 
10010 [ named<20:26> x NUM=sg PERS=3 IND=+  CARG=+ ] ; 
0:/H -> 10005 ; 
10000:RSTR/H -> 10004 ; 
10001:ARG2/NEQ -> 10003 ; 
10001:ARG1/EQ -> 10004 ; 
10002:RSTR/H -> 10003 ; 
10005:ARG1/NEQ -> 10004 ; 
10005:ARG2/NEQ -> 10010 ; 
10006:RSTR/H -> 10010 ; 
10007:ARG2/NEQ -> 10009 ; 
10007:ARG1/EQ -> 10010 ; 
10008:RSTR/H -> 10009
} '''
        dx = dmrs_str_to_xml(dstr)
        ds = xml_to_str(dx)
        
        pass

    def test_full_flow(self):
        sent = ERG.parse("My name is Sherlock Holmes")
        # tag it
        sent.tag(method=TagInfo.MFS)
        # to visko
        sx = sent.tag_xml().to_visko_xml()
        vsent = getSentenceFromXML(sx)
        # now edit the predicates
        dstr = str(vsent[0].dmrs[0])
        dstr = dstr.replace("Holmes", "Humere")
        # put the DMRS back
        vdmrs_xml = dmrs_str_to_xml(dstr)
        vdmrs_xml_str = xml_to_str(vdmrs_xml)
        vsent[0].dmrs[0] = getDMRSFromXML(vdmrs_xml)
        vsent[0].raws.clear()
        vsent[0].add_raw(vdmrs_xml_str)
        # back to ISF
        isent = vsent.to_isf()
        ip = isent[0]
        self.assertEqual(ip.dmrs().obj().ep(10010).carg, 'Humere')
        self.assertTrue(ip.dmrs().tags)
        self.assertEqual(ip.dmrs().tags[10004][0][0].synsetid, '06333653-n')
        self.assertEqual(ip.dmrs().tags[10005][0][0].synsetid, '02604760-v')

    def test_xml_to_txt(self):
        sent = getSentenceFromFile(TEST_FILE)
        logging.info("DMRS string: {}".format(sent[0].dmrs[0]))
        # tokens = simplemrs.tokenize(str(sent[0].dmrs[0]))
        # print(tokens)
        d = sent[0].dmrs[0]
        print(str(d))
        dmrs_dict = parse_dmrs_str(str(d))
        logging.info("DMRS dict: {}".format(dmrs_dict))
        # -1 because of root node (nodeid = 0)
        self.assertEqual(len(d.nodes) - 1, len(dmrs_dict['nodes']))
        self.assertEqual(len(d.links), len(dmrs_dict['links']))
        #
        dmrs_xml = dmrs_str_to_xml(str(d), sent.text)
        logging.info("DMRS XML: {}".format(dmrs_xml))


class TestDMRSParser(unittest.TestCase):

    dstr = '''dmrs {
  10000 [def_explicit_q<0:2> x pers=3 num=sg ind=+];
  10001 [poss<0:2> e sf=prop mood=indicative perf=- tense=untensed prog=-];
  10002 [pronoun_q<0:2> x pt=std num=sg pers=1];
  10003 [pron<0:2> x pt=std num=sg pers=1];
  10004 [_name_n_of_rel<3:7> x pers=3 num=sg ind=+];
  10005 [_be_v_id_rel<8:10> e sf=prop mood=indicative perf=- tense=pres prog=-];
  10006 [udef_q<11:20> x pers=3 num=pl ind=+];
  10007 [named<11:20>("Abraham") x pers=3 num=pl ind=+];
  0:/H -> 10005;
  10000:RSTR/H -> 10004;
  10001:ARG2/NEQ -> 10003;
  10001:ARG1/EQ -> 10004;
  10002:RSTR/H -> 10003;
  10005:ARG1/NEQ -> 10004;
  10005:ARG2/NEQ -> 10007;
  10006:RSTR/H -> 10007;
}'''
    dstr2 = '''dmrs {
10000 [def_explicit_q<0:2> ];
10001 [poss<0:2> e SF=prop TENSE=untensed MOOD=indicative PROG=- PERF=-];
10002 [pronoun_q<0:2> ];
10003 [pron<0:2> x NUM=sg PERS=1];
10004 [_name_n_of<3:7> x NUM=sg PERS=3 IND=+ synsetid=06333653-n synset_lemma=name synset_score=94];
10005 [_be_v_id<8:10> e SF=prop TENSE=pres MOOD=indicative PROG=- PERF=- synsetid=02604760-v synset_lemma=be synset_score=10742];
10006 [proper_q<11:26> ];
10007 [compound<11:26> e SF=prop TENSE=untensed MOOD=indicative PROG=- PERF=-];
10008 [proper_q<11:19> ];
10009 [named<11:19>("Sherlock") x NUM=sg PERS=3 IND=+];
10010 [named<20:26>("Humere") x NUM=sg PERS=3 IND=+];
0:/H -> 10005;
10000:RSTR/H -> 10004;
10001:ARG2/NEQ -> 10003;
10001:ARG1/EQ -> 10004;
10002:RSTR/H -> 10003;
10005:ARG1/NEQ -> 10004;
10005:ARG2/NEQ -> 10010;
10006:RSTR/H -> 10010;
10007:ARG2/NEQ -> 10009;
10007:ARG1/EQ -> 10010;
10008:RSTR/H -> 10009
} '''
    dstrs = (dstr, dstr2)

    def test_parse_node(self):
        for dstr in self.dstrs:
            tokens = tokenize_dmrs_str(dstr)
            dj = parse_dmrs(tokens)
            self.assertTrue(dj)
            dx = dmrs_str_to_xml(dstr)
            dobj = str_to_dmrs(dstr)
            self.assertEqual(str(getDMRSFromXML(dx)), str(dobj))


########################################################################

if __name__ == "__main__":
    unittest.main()
