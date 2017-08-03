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
import logging
from lxml import etree

from delphin.mrs import simplemrs, Pred

from .models import DMRS
from .models import Node, SortInfo, Link, Sense


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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def getSubFolders(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isdir(os.path.join(a_folder, child))]


def getFiles(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isfile(os.path.join(a_folder, child))]


def xml_to_str(xml_node, pretty_print=True):
    return etree.tostring(xml_node, pretty_print=True, encoding='utf-8').decode('utf-8')


# Visko only accept names using alphanumeric characters
NAME_RE = re.compile('^[A-Za-z0-9_]+$')


def is_valid_name(a_name):
    return NAME_RE.match(str(a_name)) if a_name is not None else False


#--------------------------------------------------------
# DMRS string (pyDelphin format) parser
#--------------------------------------------------------

def str_to_dmrs(dmrs_str, sent_text=None):
    ''' Create a DMRS object from dmrs_str (pyDelphin string format) '''
    dmrs_dict = parse_dmrs_str(dmrs_str)
    dmrs_obj = DMRS()
    for node in dmrs_dict['nodes']:
        # build node
        node_obj = Node(nodeid=node['nodeid'], cfrom=node['cfrom'], cto=node['cto'])
        dmrs_obj.nodes.append(node_obj)
        if 'carg' in node:
            node_obj.carg = node['carg']
        if node['pred'].startswith('_'):
            # realpred
            p = Pred.string_or_grammar_pred(node['pred'])
            node_obj.rplemma = p.lemma
            node_obj.rppos = p.pos
            if p.sense:
                node_obj.rpsense = p.sense
        else:
            # gpred
            node_obj.gpred = node['pred']
        # add sortinfo
        node_obj.sortinfo = SortInfo()
        if 'sortinfo' in node:
            for k, v in node['sortinfo'].items():
                setattr(node_obj.sortinfo, k, v)
        if 'sense' in node:
            node_obj.sense = Sense()
            for k, v in node['sense'].items():
                setattr(node_obj.sense, k, v)
    # create a map of nodes (by id)
    node_map = dict(list(zip([n.nodeid for n in dmrs_obj.nodes], dmrs_obj.nodes)))
    # parse all links
    for link in dmrs_dict['links']:
        if link['from'] == '0':
            # we need to create a dummy node with ID = 0
            node_zero = Node('0')
            node_zero.sortinfo = SortInfo()
            node_zero.gpred = 'unknown_root'
            node_map['0'] = node_zero
            dmrs_obj.nodes.insert(0, node_zero)
        link_obj = Link(node_map[link['from']], node_map[link['to']])
        dmrs_obj.links.append(link_obj)
        if link['rargname']:
            link_obj.rargname = link['rargname']
        if link['post']:
            link_obj.post = link['post']
    return dmrs_obj


def dmrs_str_to_xml(dmrs_str, sent_text=None):
    dmrs_dict = parse_dmrs_str(dmrs_str)
    root = etree.Element('dmrs', cfrom='-1', cto='-1')
    for node in dmrs_dict['nodes']:
        # build node
        xml_node = etree.SubElement(root, 'node', nodeid=node['nodeid'], cfrom=node['cfrom'], cto=node['cto'])
        if 'carg' in node:
            xml_node.attrib['carg'] = node['carg']
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
CARG_OPEN = '('
CARG_CLOSE = ')'


def tokenize_dmrs_str(dmrs_str):
    return simplemrs.tokenize(dmrs_str)


def parse_dmrs_str(dmrs_str):
    tokens = tokenize_dmrs_str(dmrs_str)
    return parse_dmrs(tokens)


def parse_dmrs(tokens):
    dmrs = {'nodes': [], 'links': []}
    expect(tokens, DMRS_SIG)
    expect(tokens, GROUP_OPEN)
    while len(tokens) > 2:
        nodeid = tokens.popleft()
        next_token = tokens.popleft()
        if next_token == LIST_OPEN:
            node = parse_node(nodeid, tokens)
            dmrs['nodes'].append(node)
        elif next_token == LINK_SIG:
            link = parse_link(nodeid, tokens)
            dmrs['links'].append(link)
        else:
            print("Cannot process {} from {}".format(next_token, tokens))
            break
        # next_token = tokens.popleft()
        # if next not in (ITEM_SEP, GROUP_CLOSE):
        #    raise Exception("Junk tokens at the end {}", next_token, tokens)
    if len(tokens) > 0:
        expect(tokens, GROUP_CLOSE)
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
    if tokens[0] == CARG_OPEN:
        tokens.popleft()
        carg = tokens.popleft()
        if carg.startswith('"'):
            carg = carg[1:]
        if carg.endswith('"'):
            carg = carg[:-1]
        node['carg'] = carg
        expect(tokens, CARG_CLOSE)
    if tokens[0] != LIST_CLOSE and tokens[0] in 'xeiu':
        # next one should be cvarsort
        node['sortinfo'] = {'cvarsort': tokens.popleft()}
    while tokens[0] != LIST_CLOSE:
        # parse sortinfo
        token = tokens.popleft()
        k, v = token.rsplit('=', 1)
        # if k.lower() == 'carg':
        #     # add carg to sortinfo
        #     node['carg'] = v
        if k.startswith('synset'):
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
    # take care of the last ;
    if tokens[0] == ITEM_SEP:
        tokens.popleft()
    return node


def parse_link(from_nodeid, tokens):
    rargname, post = tokens.popleft().split('/')
    expect(tokens, '-')
    expect(tokens, '>')
    to_nodeid = tokens.popleft()
    if to_nodeid.endswith(ITEM_SEP):
        to_nodeid = to_nodeid[:-1]
    elif tokens[0] == ITEM_SEP:
        tokens.popleft()
    return {'from': from_nodeid, 'to': to_nodeid, 'rargname': rargname, 'post': post}
