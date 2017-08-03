'''
XML-based data access layer for VisualKopasu project.
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

import os.path
import shutil
import gzip
import codecs
import lxml
from lxml import etree

from chirptext.anhxa import update_data
from chirptext.leutile import FileHelper
from coolisf.model import Sentence as ISFSentence

from visko.util import getLogger
from .util import getSubFolders
from .util import getFiles
from .util import is_valid_name
from .models import Sentence, Reading, DMRS, ParseRaw, Node, SortInfo, Link, Sense

logger = getLogger('visko.dao')


class XMLBiblioteche:
    def __init__(self, root):
        """
        root: path to biblioteche folder
        """
        self.root = root

    def getCorpusCollection(self, collection_name):
        bibpath = os.path.join(self.root, collection_name)
        return XMLCorpusCollection(bibpath, collection_name)


class XMLCorpusCollection:
    def __init__(self, path, name):
        """
        root: path to collection folder
        """
        self.path = path
        self.name = name

    def getCorpusDAO(self, corpus_name):
        corpus_path = os.path.join(self.path, corpus_name)
        return XMLCorpusDAO(corpus_path, corpus_name)

    def createCorpus(self, corpus_name):
        if not is_valid_name(corpus_name):
            raise Exception("Invalid corpus name (provided: {}".format(corpus_name))
        FileHelper.create_dir(os.path.join(self.path, corpus_name))

    def getCorpora(self):
        ''' Get all available corpora
        '''
        return getSubFolders(self.path)


class XMLCorpusDAO:

    def __init__(self, path, name, collection=None):
        self.path = path
        self.name = name
        self.collection = collection

    def getDocumentDAO(self, doc_name):
        doc_path = os.path.join(self.path, doc_name)
        return XMLDocumentDAO(doc_path, doc_name)

    def create_doc(self, doc_name):
        if not is_valid_name(doc_name):
            raise Exception("Invalid doc name (provided: {}".format(doc_name))
        FileHelper.create_dir(os.path.join(self.path, doc_name))


class XMLDocumentDAO:

    def __init__(self, path, name, corpus=None):
        self.path = path
        self.name = name
        self.corpus = corpus

    def getSentences(self):
        all_files = [f.split('.')[0] for f in getFiles(self.path)]
        all_files.sort()
        return all_files

    def copy_sentence(self, sent_path, sentid=None):
        if sentid is not None and (not is_valid_name(sentid)):
            raise Exception("Invalid sentenceID (provided: {}".format(sentid))
        fname = '{}.xml.gz'.format(sentid) if sentid else os.path.basename(sent_path)
        target = os.path.join(self.path, fname)
        shutil.copy2(sent_path, target)

    def save_sentence(self, xmlcontent, sentid, pretty_print=True):
        if not is_valid_name(sentid):
            raise Exception("Invalid sentenceID (provided: {})".format(sentid))
        sent_path = os.path.join(self.path, str(sentid) + '.xml.gz')
        print("Saving to {}".format(sent_path))
        with gzip.open(sent_path, 'wb') as output_file:
            if isinstance(xmlcontent, lxml.etree._Element):
                xmlcontent = lxml.etree.tostring(xmlcontent, pretty_print=pretty_print, encoding='utf-8')
            else:
                xmlcontent = xmlcontent.encode('utf-8')
            output_file.write(xmlcontent)

    def delete_sent(self, sentenceID):
        file_path = self.getPath(sentenceID)
        if not file_path:
            raise Exception("Sentence {s} does not exist (path={p})".format(s=sentenceID, p=file_path))
        else:
            os.unlink(file_path)

    def getPath(self, sentenceID=None):
        if not sentenceID:
            raise Exception("sentenceID cannot be None")
        else:
            file_name = os.path.join(self.path, str(sentenceID) + '.xml.gz')
            file_name2 = os.path.join(self.path,
                                      "%s-%s.xml.gz" % (self.name, str(sentenceID)))
            logger.debug(("Filename1: %s" % file_name))
            logger.debug(("Filename2: %s" % file_name2))

            if os.path.isfile(file_name):
                return file_name
            elif os.path.isfile(file_name2):
                return file_name2
        return None

    def getSentenceRaw(self, sentenceID):
        # Parse the file
        full_path = self.getPath(sentenceID)
        logger.debug(full_path)
        with gzip.open(full_path, 'r') as gzfile:
            return gzfile.read()

    def getSentence(self, sentenceID):
        # Read raw text from file
        full_path = self.getPath(sentenceID)
        # Parse the file
        return getSentenceFromFile(full_path)


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
        if self.raw is not None:
            logger.debug("RawXML: creating XML object from XML string")
            self.xml = etree.XML(self.raw)
        else:
            self.raw = etree.tostring(self.xml, encoding='utf-8', pretty_print=True).decode('utf-8')
        self.text = self.xml.find('text').text
        for p in self.xml.findall('reading'):
            mrs = p.findall('mrs')
            dmrs = p.findall('dmrs')
            parse = RawParse(p)
            if not mrs:
                logger.warning("MRS node does not exist")
            elif len(mrs) == 1:
                parse.mrs = mrs[0]
            else:
                logger.warning("Multiple MRS nodes")
            if dmrs is not None and len(dmrs) == 1:
                parse.dmrs = dmrs[0]
            else:
                logger.warning("Multiple DMRS nodes")
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
            sent.add(mrs_str=p.mrs.text)
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
    ''' A raw parse (e.g. ACE MRS string) '''

    def __init__(self, node=None, mrs=None, dmrs=None):
        self.node = node  # reading node
        self.mrs = mrs  # from mrs string
        self.dmrs = dmrs  # from dmrs_xml_str

    def mrs_str(self):
        return etree.tostring(self.mrs).decode('utf-8') if self.mrs is not None else ''

    def dmrs_str(self):
        return etree.tostring(self.dmrs).decode('utf-8') if self.dmrs is not None else ''


def getSentenceFromFile(file_path):
    ''' Get sentence from either .xml file or .gz file '''
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
    ''' etree node to Sentence object '''
    return getSentenceFromRawXML(RawXML(xml=xml_node))


def getSentenceFromRawXML(raw, filename=None):
    # Build Sentence object
    sid = raw.xml.attrib['id']
    text = raw.xml.find('text').text
    sentence = Sentence(sid, text)
    if filename:
        sentence.filename = filename

    for idx, parse in enumerate(raw):
        reading = Reading()
        reading.rid = parse.node.attrib['id']
        reading.mode = parse.node.attrib['mode']
        if parse.mrs is not None:
            # add raw MRS
            reading.raws.append(ParseRaw(parse.mrs.text, rtype=ParseRaw.MRS))
        if parse.dmrs is not None:
            reading.raws.append(ParseRaw(parse.dmrs_str(), rtype=ParseRaw.XML))

        sentence.readings.append(reading)
        # XXX: parse all synthetic trees

        # parse all DMRS
        dmrs = getDMRSFromXML(parse.dmrs)
        reading.dmrs.append(dmrs)
    return sentence


def getDMRSFromXMLString(xmlcontent):
    '''
        Get DMRS object from XML string
    '''
    root = etree.XML(xmlcontent)
    if root.tag == 'reading':
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
        update_data(node_tag.attrib, temp_node, *(x for x in ('surface', 'base', 'carg') if x in node_tag.attrib))
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
            logger.debug("Using gold => %s" % (sense_info.synsetid))
            pass
        else:
            sense_tag = node_tag.find('sense')
            if sense_tag is not None:
                sense_info = Sense()
                update_data(sense_tag.attrib, sense_info)
                temp_node.sense = sense_info

        # TODO: parse sort info
        sortinfo_tag = node_tag.find("sortinfo")
        if sortinfo_tag is not None:
            sortinfo = SortInfo()
            update_data(sortinfo_tag.attrib, sortinfo)
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
            logger.error("ERROR: Invalid nodeID [%s -> %s] in link_tag: %s" % (fromNodeID, toNodeID, link_tag))
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
    # finished, add dmrs object to reading
    return dmrs
