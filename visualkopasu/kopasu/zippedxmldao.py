'''
Zipped XML-based data access layer for VisualKopasu project.
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

import gzip
import os.path
import logging
import sys
from zipfile import ZipFile
from gzip import GzipFile
import io
from xml.etree import ElementTree as ETree

from .models import Sentence, Representation, DMRS
from .models import Node, SortInfo, Gpred, Link, RealPred, Post, Rargname
"""
XML Document repository 
"""
class ZippedXMLDocumentDAO():
    """
    input: path to folder stores the Sentence files
    """
    def __init__(self, config):
        self.config = config
        if self.config['dbname'] is None or len(self.config['dbname']) == 0:
            self.config['dbname'] = self.config['corpus']
        self.namelist = None
        self.documents = None
        self.package_file = ZipFile(self.getPath(), 'r')
    
    def read_package(self):
        if self.namelist is None:
            package_path = self.getPath()
            self.namelist = self.package_file.namelist()
        return self.namelist
    
    def read_documents(self):
        if self.documents is None:
            
            self.documents = []
            for name in self.read_package():
                document = name.split("/")[0]
                if document not in self.documents:
                    self.documents.append(document)
        return self.documents
    
    def getAllDocuments(self):
        return self.read_documents()
    
    def getAllSentences(self, doc_name=None):
        sentence_list = []

        for name in self.read_package():
            parts = name.split("/")
            this_doc_name = parts[0]
            this_sentence_name = parts[1].split('.')[0]
            if not doc_name or this_doc_name == doc_name:
                sentence_list.append(this_sentence_name)
        sentence_list.sort()
        return sentence_list
    
    def getPath(self, sentenceID = None):
        return os.path.join(self.config['root'], self.config['dbname'])
    
    def searchSentence(self, post):
        return None # Not supported
    
    def getSentenceRaw(self, sentenceID, documentID=None):
        package_path = self.getPath()
        if documentID is None:
            documentID = self.config['document']
        content=None
        file_name = documentID + "/" + str(sentenceID) + ".xml.gz"
        try:
            content = GzipFile(fileobj=io.StringIO(self.package_file.read(file_name)), mode='rb').read()
        except Exception as e:
            try:
                file_name2 = documentID + "/" + documentID + "-" + str(sentenceID) + '.xml.gz'
                content = GzipFile(fileobj=io.StringIO(self.package_file.read(file_name2)), mode='rb').read()
            except:
                pass
        return content

    def getDMRSRaw(self, sentenceID, representationID, documentID=None, dmrs_only = True):
        # Read raw text
        content = self.getSentenceRaw(sentenceID, documentID)
        if content is None:
            return None
        root = ETree.fromstring(content)

        result_set = []
        q = "representation[@id='" + representationID + "']" if representationID else "representation"
        print(("Query = %s" % q))
        elements = root.findall(q)
        print(("Found element: %s" % len(elements)))
        # for each dmrs
        for element in elements:
            if dmrs_only:
                for child in list(element):
                    if child.tag != 'dmrs':
                        element.remove(child)
            # Convert element to XML text
            element_xml = ETree.tostring(element, encoding="utf-8", method="xml").replace('</dmrs><', '</dmrs>\n<').replace('><dmrs', '>\n<dmrs')
            result_set.append(element_xml)
        return result_set
    
    def getSentence(self, sentenceID):
        # Read raw setntence text & parse it
        content = self.getSentenceRaw(sentenceID)
        #root = ETree.parse(full_path).getroot()
        root = ETree.fromstring(content)
        
        # Build Sentence object
        sid = root.attrib['id']
        text = root.find('text').text
        sentence = Sentence(sid, text)
        
        for representation_tag in root.findall('representation'):
            representation = Representation()
            representation.update_field("rid", "id", representation_tag.attrib)
            representation.update_field("mode", "", representation_tag.attrib)
            #representation.update_from(representation_tag.attrib)
            sentence.representations.append(representation)
            # XXX: parse all synthetic trees
            
            # parse all DMRS
            dmrs_list = representation_tag.findall('dmrs')
            for dmrs_tag in dmrs_list:
                dmrs = DMRS()
                dmrs.ident = dmrs_tag.attrib['ident'] if 'ident' in dmrs_tag else ''
                dmrs.cfrom = dmrs_tag.attrib['cfrom'] if 'cfrom' in dmrs_tag else ''
                dmrs.cto = dmrs_tag.attrib['cto'] if 'cto' in dmrs_tag else ''
                dmrs.surface = dmrs_tag.attrib['surface'] if 'surface' in dmrs_tag else ''
                
                # parse all nodes inside
                for node_tag in dmrs_tag.findall('node'):
                    temp_node = Node(node_tag.attrib['nodeid'], node_tag.attrib['cfrom'], node_tag.attrib['cto'])
                    #temp_node.update_from(node_tag.attrib)
                    temp_node.update_field('surface', '', node_tag.attrib)
                    temp_node.update_field('base', '', node_tag.attrib)
                    temp_node.update_field('carg', '', node_tag.attrib)
                    
                    # TODO: parse sort info
                    sortinfo_tag = node_tag.find("sortinfo")
                    if sortinfo_tag != None:
                        sortinfo = SortInfo()
                        sortinfo.update_from(sortinfo_tag.attrib)
                        temp_node.sortinfo = sortinfo
                    # FIXME: parse gpred
                    gpred_tag = node_tag.find("gpred")
                    if gpred_tag != None:
                        gpred = Gpred(gpred_tag.text)
                        temp_node.gpred = gpred
                    # TODO: parse realpred
                    realpred_tag = node_tag.find("realpred")
                    if realpred_tag != None:
                        realpred = RealPred()
                        realpred.update_from(realpred_tag.attrib)
                        temp_node.realpred = realpred
                    # Completed parsing, add the node_tag to DMRS object 
                    dmrs.nodes.append(temp_node)
                    # end for nodes
                # create a map of nodes (by id)
                node_map = dict(list(zip([n.nodeid for n in dmrs.nodes], dmrs.nodes)))
            
                # parse all links inside
                for link_tag in dmrs_tag.findall('link'):
                    fromNode = node_map[link_tag.attrib['from']]
                    toNode = node_map[link_tag.attrib['to']]
                    temp_link = Link(fromNode, toNode)
                    
                    # TODO: parse post
                    post_tag = link_tag.find("post")
                    if post_tag != None:
                        post = Post(post_tag.text)
                        temp_link.post = post
                    # TODO: parse rargname
                    rargname_tag = link_tag.find("rargname")
                    if rargname_tag != None:
                        rargname = Rargname(rargname_tag.text)
                        temp_link.rargname = rargname
                    # end for link_tag
                    dmrs.links.append(temp_link)
                # finished, add dmrs object to representation
            representation.dmrs.append(dmrs)
            # add representation to Sentence
        # Return
        return sentence
