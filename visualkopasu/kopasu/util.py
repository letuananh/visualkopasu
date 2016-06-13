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

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2016, Visual Kopasu"
__credits__ = []
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import logging
from xml.etree import ElementTree as ETree

from .models import Sentence, Interpretation, DMRS
from .models import Node, SortInfo, Gpred, Link, RealPred, Post, Rargname, Sense

def getDMRSFromXMLString(xmlcontent):
    root = ETree.fromstring(xmlcontent)
    if root.tag == 'interpretation':
        root = root.findall('dmrs')[0]
    return getDMRSFromXML(root)

def getDMRSFromXML(dmrs_tag):
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

        # Parse sense info
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
        if gpred_tag != None:
            gpred = Gpred(gpred_tag.text)
            temp_node.gpred = gpred
        # TODO: parse realpred
        realpred_tag = node_tag.find("realpred")
        if realpred_tag is not None:
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
        fromNodeID = link_tag.attrib['from']
        toNodeID   = link_tag.attrib['to']
        if fromNodeID not in node_map or toNodeID not in node_map:
            logging.error("ERROR: Invalid nodeID [%s=>%s] in link_tag: %s" % (fromNodeID, toNodeID, link_tag))
        else:
            fromNode = node_map[fromNodeID]
            toNode = node_map[toNodeID]
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
    # finished, add dmrs object to interpretation
    return dmrs

def getSentenceFromXMLString(xmlcontent):
    root = ETree.fromstring(xmlcontent)

    # Build Sentence object
    sid = root.attrib['id']
    text = root.find('text').text
    sentence = Sentence(sid, text)

    for interpretation_tag in root.findall('interpretation'):
        interpretation = Interpretation()
        interpretation.update_field("rid", "id", interpretation_tag.attrib)
        interpretation.update_field("mode", "", interpretation_tag.attrib)
        #interpretation.update_from(interpretation_tag.attrib)
        sentence.interpretations.append(interpretation)
        # XXX: parse all synthetic trees

        # parse all DMRS
        dmrs_list = interpretation_tag.findall('dmrs')
        for dmrs_tag in dmrs_list:
            dmrs = getDMRSFromXML(dmrs_tag)
        interpretation.dmrs.append(dmrs)
        # add interpretation to Sentence
    # Return
    return sentence
