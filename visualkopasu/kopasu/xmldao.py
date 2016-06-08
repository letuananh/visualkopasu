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

import gzip
import os.path
import logging
from xml.etree import ElementTree as ETree

from .models import Sentence, Representation, DMRS
from .models import Node, SortInfo, Gpred, Link, RealPred, Post, Rargname

"""
XML Document repository 
"""
class XMLDocumentDAO():
    """
    input: path to folder stores the Sentence files
    """
    def __init__(self, config):
        self.config = config
        pass
    
    def getAllSentences(self):
        folder_path = self.getPath()
        all_files = [ f.split('.')[0] for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path,f)) ]
        all_files.sort()
        return all_files
    
    def getPath(self, sentenceID = None):
        if sentenceID:
            file_name = os.path.join(self.config['root'], self.config['corpus'], self.config['document'], str(sentenceID) + '.xml.gz')
            file_name2 = os.path.join(self.config['root'], self.config['corpus'], self.config['document'], self.config['document'] + "-" + str(sentenceID) + '.xml.gz')
            file_name3 = os.path.join(self.config['root'], self.config['corpus'], self.config['document'], str(sentenceID) + '.gz')
            print(("Filename1: %s" % file_name))
            print(("Filename2: %s" % file_name2))
            print(("Filename3: %s" % file_name3))
            if os.path.isfile(file_name):
                return file_name
            elif os.path.isfile(file_name2):
                return file_name2
            else:
                return file_name3
        else:
            return os.path.join(self.config['root'], self.config['corpus'], self.config['document'])
    
    def searchSentence(self, post):
        sids = self.getAllSentences()
        sentences = []
        for sid in sids:
            sentence = self.getSentence(sid)
            active = sentence.getActiveRepresentation()
            for dmrs in active.dmrs:
                for link in dmrs.links:
                    if link.post.value == post:
                        sentences.append(sid)
                        print(("DEBUG: found -> " + str(sid)))
        return sentences
    
    def getSentenceRaw(self, sentenceID, documentID=None):
        # Read raw text from file
        full_path = self.getPath(sentenceID)
        print(("sentenceID = " + sentenceID))
        # Parse the file
        content = gzip.open(full_path, 'r').read()
        return content

    def getDMRSRaw(self, sentenceID, representationID, documentID=None, dmrs_only=True):
        self.config['document'] = documentID
        # Read raw text from file
        print(("SentenceID = %s " % sentenceID))
        full_path = self.getPath(sentenceID)

        # Parse the file
        content = gzip.open(full_path, 'r').read()
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
            element_xml = ETree.tostring(element, encoding="utf-8", method="xml").decode('utf-8')
            element_xml = element_xml.replace('</dmrs><', '</dmrs>\n<').replace('><dmrs', '>\n<dmrs')
            result_set.append(element_xml)
        return result_set
    
    def getSentence(self, sentenceID):
        # Read raw text from file
        full_path = self.getPath(sentenceID)

        # Parse the file
        content = gzip.open(full_path, 'r').read()
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
                dmrs.ident = dmrs_tag.attrib['ident'] if 'ident' in dmrs_tag.attrib else ''
                dmrs.cfrom = dmrs_tag.attrib['cfrom'] if 'cfrom' in dmrs_tag.attrib else ''
                dmrs.cto = dmrs_tag.attrib['cto'] if 'cto' in dmrs_tag.attrib else ''
                dmrs.surface = dmrs_tag.attrib['surface'] if 'surface' in dmrs_tag.attrib else ''
                
                # parse all nodes inside
                for node_tag in dmrs_tag.findall('node'):
                    temp_node = Node(node_tag.attrib['nodeid'], node_tag.attrib['cfrom'], node_tag.attrib['cto'])
                    #temp_node.update_from(node_tag.attrib)
                    temp_node.update_field('surface', '', node_tag.attrib)
                    temp_node.update_field('base', '', node_tag.attrib)
                    temp_node.update_field('carg', '', node_tag.attrib)
                    #temp_node.carg = node_tag.attrib['carg'] if node_tag.attrib.has_key('carg') else ''
                    
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
