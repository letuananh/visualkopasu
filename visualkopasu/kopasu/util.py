'''
Util for VisualKopasu project.
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

########################################################################

import os
import re
import codecs
import logging
import gzip
from lxml import etree
from delphin.mrs import simplemrs, Pred
from .models import Sentence, Interpretation, DMRS, ParseRaw
from .models import Node, SortInfo, Link, Sense

from coolisf.model import Sentence as ISFSentence

########################################################################

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2016, Visual Kopasu"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################


def getSubFolders(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isdir(os.path.join(a_folder, child))]


def getFiles(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isfile(os.path.join(a_folder, child))]


class RawXML(object):
    ''' Visko sentence in RAW XML format (preprocessor)
    '''

    def __init__(self, raw=None, xml=None):
        self.raw = raw  # XML string
        self.text = ''
        self.xml = xml
        self.parses = []
        if self.raw is not None or self.xml is not None:
            self.parse()

    def parse(self):
        if self.raw:
            self.xml = etree.XML(self.raw)
        else:
            self.raw = etree.tostring(self.xml, encoding='utf-8', pretty_print=True).decode('utf-8')
        self.text = self.xml.find('text').text
        for p in self.xml.findall('interpretation'):
            mrs = p.findall('mrs')
            dmrs = p.findall('dmrs')
            parse = RawParse(p)
            if mrs and len(mrs) == 1:
                parse.mrs = mrs[0]
            else:
                logging.warning("Multiple MRS nodes")
            if dmrs and len(dmrs) == 1:
                parse.dmrs = dmrs[0]
            else:
                logging.warning("Multiple DMRS nodes")
            self.parses.append(parse)

    def __iter__(self):
        return iter(self.parses)

    def __len__(self):
        return len(self.parses)

    def __getitem__(self, key):
        return self.parses[key]

    def __str__(self):
        return "{} ({} parse(s))".format(self.text, len(self))

    def to_isf(self):
        sent = ISFSentence(self.text)
        for p in self.parses:
            sent.add_from_xml(p.dmrs_str())
        return sent

    @staticmethod
    def from_file(filename):
        ''' Read RawXML from .xml file or .gz file
        '''
        if filename.endswith('.gz'):
            with gzip.open(filename, 'rt', encoding='utf-8') as gzfile:
                return RawXML(gzfile.read())
        else:
            with codecs.open(filename, encoding='utf-8') as infile:
                return RawXML(infile.read())


class RawParse(object):

    def __init__(self, node=None, mrs=None, dmrs=None):
        self.node = node  # interpretation node
        self.mrs = mrs
        self.dmrs = dmrs

    def mrs_str(self):
        return etree.tostring(self.mrs).decode('utf-8') if self.mrs is not None else ''

    def dmrs_str(self):
        return etree.tostring(self.dmrs).decode('utf-8') if self.dmrs is not None else ''


def getDMRSFromXMLString(xmlcontent):
    '''
        Get DMRS object from XML string
    '''
    root = etree.XML(xmlcontent)
    if root.tag == 'interpretation':
        root = root.findall('dmrs')[0]
    return getDMRSFromXML(root)


def getDMRSFromXML(dmrs_tag):
    ''' Get DMRS from XML node
    '''
    dmrs = DMRS()
    dmrs.ident = dmrs_tag.attrib['ident'] if 'ident' in dmrs_tag.attrib else ''
    dmrs.cfrom = dmrs_tag.attrib['cfrom'] if 'cfrom' in dmrs_tag.attrib else ''
    dmrs.cto = dmrs_tag.attrib['cto'] if 'cto' in dmrs_tag.attrib else ''
    dmrs.surface = dmrs_tag.attrib['surface'] if 'surface' in dmrs_tag.attrib else ''

    # parse all nodes inside
    for node_tag in dmrs_tag.findall('node'):
        temp_node = Node(node_tag.attrib['nodeid'], node_tag.attrib['cfrom'], node_tag.attrib['cto'])
        # temp_node.update_from(node_tag.attrib)
        temp_node.update_field('surface', '', node_tag.attrib)
        temp_node.update_field('base', '', node_tag.attrib)
        temp_node.update_field('carg', '', node_tag.attrib)
        # temp_node.carg = node_tag.attrib['carg'] if node_tag.attrib.has_key('carg') else ''

        # Parse sense info
        sensegold_tag = node_tag.find('sensegold')
        if sensegold_tag is not None:
            # if we have sensegold, use it instead
            sense_info = Sense()
            sense_info.lemma = sensegold_tag.attrib['lemma']
            sense_info.synsetid = sensegold_tag.attrib['synsetid']
            sense_info.pos = sense_info.synsetid[-1]
            sense_info.score = '999'
            temp_node.sense = sense_info
            logging.debug("Using gold => %s" % (sense_info.synsetid))
            pass
        else:
            sense_tag = node_tag.find('sense')
            if sense_tag is not None:
                sense_info = Sense()
                sense_info.update_from(sense_tag.attrib)
                temp_node.sense = sense_info

        # TODO: parse sort info
        sortinfo_tag = node_tag.find("sortinfo")
        if sortinfo_tag is not None:
            sortinfo = SortInfo()
            sortinfo.update_from(sortinfo_tag.attrib)
            temp_node.sortinfo = sortinfo
        # FIXME: parse gpred
        gpred_tag = node_tag.find("gpred")
        if gpred_tag is not None:
            temp_node.gpred = gpred_tag.text
        # TODO: parse realpred
        realpred_tag = node_tag.find("realpred")
        if realpred_tag is not None:
            if 'lemma' in realpred_tag.attrib:
                temp_node.rplemma = realpred_tag.attrib['lemma']
            if 'pos' in realpred_tag.attrib:
                temp_node.rppos = realpred_tag.attrib['pos']
            if 'sense' in realpred_tag.attrib:
                temp_node.rpsense = realpred_tag.attrib['sense']
        # Completed parsing, add the node_tag to DMRS object
        dmrs.nodes.append(temp_node)
        # end for nodes
    # create a map of nodes (by id)
    node_map = dict(list(zip([n.nodeid for n in dmrs.nodes], dmrs.nodes)))

    # parse all links inside
    for link_tag in dmrs_tag.findall('link'):
        fromNodeID = link_tag.attrib['from']
        toNodeID = link_tag.attrib['to']
        if fromNodeID == '0':
            # we need to create a dummy node with ID = 0
            node_zero = Node('0')
            node_zero.sortinfo = SortInfo()
            node_zero.gpred = 'unknown_root'
            node_map['0'] = node_zero
            dmrs.nodes.append(node_zero)
        if fromNodeID not in node_map or toNodeID not in node_map:
            logging.error("ERROR: Invalid nodeID [%s=>%s] in link_tag: %s" % (fromNodeID, toNodeID, link_tag))
        else:
            fromNode = node_map[fromNodeID]
            toNode = node_map[toNodeID]
            temp_link = Link(fromNode, toNode)

            # TODO: parse post
            post_tag = link_tag.find("post")
            if post_tag is not None:
                temp_link.post = post_tag.text
            rargname_tag = link_tag.find("rargname")
            if rargname_tag is not None:
                temp_link.rargname = rargname_tag.text
            # end for link_tag
            dmrs.links.append(temp_link)
    # finished, add dmrs object to interpretation
    return dmrs


def getSentenceFromFile(file_path):
    raw = RawXML.from_file(file_path)  # supports both .xml file and .gz file now
    filename = os.path.basename(file_path)
    return getSentenceFromRawXML(raw, filename)


def getSentenceFromXMLString(xmlcontent):
    if isinstance(xmlcontent, etree._Element):
        raw = RawXML(xml=xmlcontent)
    else:
        raw = RawXML(raw=xmlcontent)
    return getSentenceFromRawXML(raw)


def getSentenceFromXML(xml_node):
    return getSentenceFromRawXML(RawXML(xml=xml_node))


def getSentenceFromRawXML(raw, filename=None):
    # Build Sentence object
    sid = raw.xml.attrib['id']
    text = raw.xml.find('text').text
    sentence = Sentence(sid, text)
    if filename:
        sentence.filename = filename

    for idx, parse in enumerate(raw):
        interpretation = Interpretation()
        interpretation.update_field("rid", "id", parse.node.attrib)
        interpretation.update_field("mode", "", parse.node.attrib)
        if parse.mrs is not None:
            # add raw MRS
            interpretation.raws.append(ParseRaw(parse.mrs.text, rtype=ParseRaw.MRS))
        if parse.dmrs is not None:
            interpretation.raws.append(ParseRaw(parse.dmrs_str(), rtype=ParseRaw.XML))

        # interpretation.update_from(interpretation_tag.attrib)
        sentence.interpretations.append(interpretation)
        # XXX: parse all synthetic trees

        # parse all DMRS
        dmrs = getDMRSFromXML(parse.dmrs)
        interpretation.dmrs.append(dmrs)
    return sentence


# Visko only accept names using alphanumeric characters
NAME_RE = re.compile('^[a-z0-9_]+$')


def is_valid_name(a_name):
    return NAME_RE.match(str(a_name)) if a_name is not None else False

###############################################################
# DMRS parser


def xml_to_str(xml_node, pretty_print=True):
    return etree.tostring(xml_node, pretty_print=True, encoding='utf-8').decode('utf-8')


def dmrs_str_to_xml(dmrs_str, sent_text=None):
    dmrs_dict = parse_dmrs_str(dmrs_str)
    root = etree.Element('dmrs', cfrom='-1', cto='-1')
    for node in dmrs_dict['nodes']:
        # build node
        cfrom = int(node['cfrom'])
        cto = int(node['cto'])
        xml_node = etree.SubElement(root, 'node', nodeid=node['nodeid'], cfrom=node['cfrom'], cto=node['cto'])
        if 'carg' in node and node['carg'] == '+':
            if sent_text is not None:
                xml_node.attrib['carg'] = '"{}"'.format(sent_text[cfrom:cto])
        if node['pred'].startswith('_'):
            # realpred
            p = Pred.string_or_grammar_pred(node['pred'])
            if p.sense:
                etree.SubElement(xml_node, 'realpred', lemma=p.lemma, pos=p.pos, sense=p.sense)
            else:
                etree.SubElement(xml_node, 'realpred', lemma=p.lemma, pos=p.pos)
        else:
            # gpred
            gpred = etree.SubElement(xml_node, 'gpred')
            gpred.text = node['pred']
        # add sortinfo
        xml_sortinfo = etree.SubElement(xml_node, 'sortinfo')
        if 'sortinfo' in node:
            for k, v in node['sortinfo'].items():
                xml_sortinfo.attrib[k] = v
        if 'sense' in node:
            xml_sense = etree.SubElement(xml_node, 'sense')
            for k, v in node['sense'].items():
                xml_sense.attrib[k] = v
        # add ISF sense
    for link in dmrs_dict['links']:
        xml_link = etree.SubElement(root, 'link')
        xml_link.attrib['from'] = link['from']
        xml_link.attrib['to'] = link['to']
        etree.SubElement(xml_link, 'rargname').text = link['rargname']
        etree.SubElement(xml_link, 'post').text = link['post']
    return root
    # return etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8')


DMRS_SIG = 'dmrs'
LIST_OPEN = '['
LIST_CLOSE = ']'
GROUP_OPEN = '{'
GROUP_CLOSE = '}'
ITEM_SEP = ';'
CFROM = '<'
FROMTOSEP = ':'
CTO = '>'
LINK_SIG = ':'


def parse_dmrs_str(dmrs_str):
    tokens = simplemrs.tokenize(dmrs_str)
    if tokens.popleft() == DMRS_SIG and tokens.popleft() == GROUP_OPEN:
        # parse dmrs
        dmrs = parse_dmrs(tokens)
        return dmrs
    else:
        raise Exception("Invalid DMRS string")


def parse_dmrs(tokens):
    dmrs = {'nodes': [], 'links': []}
    while len(tokens) > 0:
        nodeid = tokens.popleft()
        next = tokens.popleft()
        if next == LIST_OPEN:
            node = parse_node(nodeid, tokens)
            dmrs['nodes'].append(node)
        elif next == LINK_SIG:
            link = parse_link(nodeid, tokens)
            dmrs['links'].append(link)
        else:
            break
        next = tokens.popleft()
        if next not in (ITEM_SEP, GROUP_CLOSE):
            raise Exception("Junk tokens at the end")
    return dmrs


def expect(tokens, expected, message=None):
    actual = tokens.popleft()
    if actual != expected:
        if message:
            raise Exception(message)
        else:
            raise Exception("Expected {}, actual {}".format(expected, actual))
    else:
        return actual


def parse_node(nodeid, tokens):
    pred = tokens.popleft()
    expect(tokens, CFROM)
    cfrom = tokens.popleft()
    expect(tokens, FROMTOSEP)
    cto = tokens.popleft()
    expect(tokens, CTO)
    node = {'pred': pred, 'nodeid': nodeid, 'cfrom': cfrom, 'cto': cto}
    if tokens[0] != LIST_CLOSE:
        # next one should be cvarsort
        node['sortinfo'] = {'cvarsort': tokens.popleft()}
    while tokens[0] != LIST_CLOSE:
        # parse sortinfo
        token = tokens.popleft()
        k, v = token.rsplit('=', 1)
        if k == 'CARG':
            # add carg to sortinfo
            node['carg'] = v
        elif k.startswith('synset'):
            if 'sense' not in node:
                node['sense'] = {}
            if k == 'synsetid':
                node['sense'][k] = v
            else:
                node['sense'][k[7:]] = v
        else:
            # add to sortinfo
            node['sortinfo'][k.lower()] = v
        pass
    expect(tokens, LIST_CLOSE)
    return node


def parse_link(from_nodeid, tokens):
    rargname, post = tokens.popleft().split('/')
    expect(tokens, '-')
    expect(tokens, '>')
    to_nodeid = tokens.popleft()
    return {'from': from_nodeid, 'to': to_nodeid, 'rargname': rargname, 'post': post}
