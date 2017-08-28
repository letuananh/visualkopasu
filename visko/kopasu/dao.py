'''
Data access layer for VisualKopasu project.
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
import os.path
import logging
from visko.util import getLogger
from visko.kopasu.util import is_valid_name

from puchikarui import Schema

from .models import Corpus
from .models import Document
from .models import Sentence
from .models import Reading
from .models import DMRS
from .models import ParseRaw
from .models import Node
from .models import Sense
from .models import SortInfo
from .models import Link
from .models import GpredValue
from .models import Lemma
from .models import Word, Concept, CWLink


########################################################################

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2012, Visual Kopasu"
__credits__ = ["Fan Zhenzhen", "Francis Bond", "Mathieu Morey"]
__license__ = "GPL"
__version__ = "0.2"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

#----------------------------------------------------------------------
# Configuration
#----------------------------------------------------------------------

logger = getLogger('visko.dao')
MY_DIR = os.path.dirname(os.path.realpath(__file__))
INIT_SCRIPT = os.path.join(MY_DIR, 'scripts', 'sqlite3', 'create.sql')


class ViskoSchema(Schema):

    def __init__(self, data_source):
        Schema.__init__(self, data_source=data_source, setup_file=INIT_SCRIPT)
        self.add_table('corpus', ['ID', 'name', 'title'], proto=Corpus).set_id('ID')
        self.add_table('document', ['ID', 'name', 'corpusID', 'title',
                                    'grammar', 'tagger', 'parse_count', 'lang'],
                       proto=Document, alias='doc').set_id('ID')
        self.add_table('sentence', ['ID', 'ident', 'text', 'documentID', 'flag', 'comment'],
                       proto=Sentence).set_id('ID')
        self.add_table('reading', ['ID', 'ident', 'mode', 'sentenceID', 'comment'],
                       proto=Reading).set_id('ID').field_map(ident='rid')
        self.add_table('dmrs', ['ID', 'ident', 'cfrom', 'cto', 'surface', 'readingID'],
                       proto=DMRS).set_id('ID')
        self.add_table('parse_raw', ['ID', 'ident', 'text', 'rtype', 'readingID'],
                       proto=ParseRaw).set_id('ID')
        # Node related tables
        self.add_table('dmrs_node', ['ID', 'nodeid', 'cfrom', 'cto', 'surface', 'base',
                                     'carg', 'dmrsID', 'rplemmaID', 'rppos', 'rpsense',
                                     'gpred_valueID', 'synsetid', 'synset_score'],
                       proto=Node, alias='node').set_id('ID')
        self.add_table('dmrs_node_sortinfo', ['ID', 'cvarsort', 'num', 'pers', 'gend', 'sf',
                                              'tense', 'mood', 'prontype', 'prog', 'perf',
                                              'ind', 'dmrs_nodeID'],
                       proto=SortInfo, alias='sortinfo').set_id('ID')
        self.add_table('dmrs_node_gpred_value', ['ID', 'value'],
                       proto=GpredValue, alias='gpval').set_id('ID')
        self.add_table('dmrs_node_realpred_lemma', ['ID', 'lemma'],
                       proto=Lemma, alias='rplemma').set_id('ID')
        # Link related tables
        self.add_table('dmrs_link', ['ID', 'fromNodeID', 'toNodeID', 'dmrsID', 'post', 'rargname'],
                       proto=Link, alias='link').set_id('ID')
        # Human annotation related tables
        self.add_table('word', ['ID', 'sid', 'widx', 'word', 'lemma', 'pos', 'cfrom', 'cto', 'comment'],
                       proto=Word).set_id('ID')
        self.add_table('concept', ['ID', 'sid', 'cidx', 'clemma', 'tag', 'flag', 'comment'],
                       proto=Concept).set_id('ID')
        self.add_table('cwl', ['cid', 'wid'],
                       proto=CWLink)


class CachedTable():
    '''
    ORM cache
    @auto_fill: Auto select all objects to cache when the cache is created
    '''
    def __init__(self, table, cache_by_field="value", ctx=None, auto_fill=True):
        self.cacheMap = {}
        self.cacheMapByID = {}
        self.table = table
        self.cache_by_field = cache_by_field
        if auto_fill:
            instances = self.table.select(ctx=ctx)
            if instances is not None:
                for instance in instances:
                    self.cache(instance)

    def cache(self, instance):
        if instance:
            key = getattr(instance, self.cache_by_field)
            if key not in self.cacheMap:
                self.cacheMap[key] = instance
            else:
                logger.debug(("Cache error: key [%s] exists!" % key))

            key = tuple(getattr(instance, c) for c in self.table.id_cols)
            if key not in self.cacheMapByID:
                self.cacheMapByID[key] = instance
            else:
                logger.debug(("Cache error: ID [%s] exists!" % key))

    def by_value(self, value, new_object=None, ctx=None):
        if value not in self.cacheMap:
            # insert a new record
            if new_object is None:
                # try to select from database first
                results = self.table.select_single("{f}=?".format(f=self.cache_by_field), (value,), ctx=ctx)
                if not results:
                    # create a new instance
                    new_object = self.table.to_obj((value,), (self.cache_by_field,))
                    self.table.save(new_object, ctx=ctx)
                    # select the instance again
                    new_object = self.table.select_single("{f}=?".format(f=self.cache_by_field), (value,), ctx=ctx)
                else:
                    new_object = results  # Use the object from DB
            self.cache(new_object)
        return self.cacheMap[value]

    def by_id(self, *ID, ctx=None):
        k = tuple(ID)
        if k not in self.cacheMapByID:
            # select from database
            obj = self.table.by_id(*ID, ctx=ctx)
            self.cache(obj)
        return self.cacheMapByID[k]


class SQLiteCorpusCollection(object):
    def __init__(self, path):
        self.path = path

    def getCorpusDAO(self, collection_name, auto_fill=False):
        collection_db_path = os.path.join(self.path, collection_name + '.db')
        return SQLiteCorpusDAO(collection_db_path, collection_name, auto_fill=auto_fill)


class SQLiteCorpusDAO(ViskoSchema):

    def __init__(self, db_path, name, auto_fill=False):
        super().__init__(db_path)
        self.name = name
        self.lemmaCache = CachedTable(self.rplemma, "lemma", auto_fill=auto_fill)
        self.gpredCache = CachedTable(self.gpval, "value", auto_fill=auto_fill)

    @property
    def db_path(self):
        return self.ds.path

    def getCorpora(self):
        return self.corpus.select()

    def getCorpus(self, corpus_name):
        # corpus name is unique
        return self.corpus.select_single('name=?', (corpus_name,))

    def getCorpusByID(self, corpusID):
        return self.corpus.by_id(corpusID)

    def create_corpus(self, corpus_name, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.create_corpus(corpus_name, ctx=ctx)
        # ctx was ensured
        if not is_valid_name(corpus_name):
            raise Exception("Invalid corpus name (provided: {}) - Visko only accept names using alphanumeric characters".format(corpus_name))
        corpus = Corpus(corpus_name)
        corpus.ID = ctx.corpus.save(corpus)
        return corpus

    def saveDocument(self, doc, *fields, ctx=None):
        if not is_valid_name(doc.name):
            raise ValueError("Invalid doc name (provided: {}) - Visko only accept names using alphanumeric characters".format(doc.name))
        else:
            doc.ID = self.doc.save(doc, *fields, ctx=ctx)
        return doc

    def getDocumentOfCorpus(self, corpusID):
        return self.doc.select('corpusID=?', (corpusID,))

    def getDocument(self, docID):
        return self.doc.by_id(docID)

    def getDocumentByName(self, doc_name):
        return self.doc.select('name=?', (doc_name,))

    def getSentences(self, docID, flag=None, add_dummy_parses=True):
        where = 'documentID = ?'
        params = [docID]
        if flag:
            where += ' AND flag = ?'
            params.append(flag)
        if add_dummy_parses:
            query = '''
            SELECT sentence.*, count(reading.ID) AS 'parse_count'
            FROM sentence LEFT JOIN reading
            ON sentence.ID = reading.sentenceID
            WHERE {where}
            GROUP BY sentenceID ORDER BY sentence.ID;
            '''.format(where=where)
            with self.ctx() as ctx:
                rows = ctx.execute(query, params)
                sents = []
                for row in rows:
                    sent = self.sentence.to_obj(row)
                    sent.readings = [None] * row['parse_count']
                    sents.append(sent)
                return sents
        else:
            return self.Sentence.select(where, params)

    def query(self, query_obj):
        return self.ds.select(query_obj.query, query_obj.params)

    def note_sentence(self, sent_id, comment, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.note_sentence(sent_id, comment, ctx=ctx)
        # save comments
        return ctx.sentence.update((comment,), 'ID=?', (sent_id,), ['comment'])

    def read_note_sentence(self, sent_id, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.read_note_sentence(sent_id, ctx=ctx)
        return ctx.sentence.by_id(sent_id, columns=['comment']).comment

    def save_sent(self, a_sentence, ctx=None):
        """
        Save sentence object (with all DMRSes, raws & shallow readings inside)
        """
        # validations
        if a_sentence is None:
            raise ValueError("Sentence object cannot be None")
        if ctx is None:
            with self.ctx() as ctx:
                return self.save_sent(a_sentence, ctx=ctx)
        # ctx is not None now
        if not a_sentence.ID:
            # choose a new ident
            if a_sentence.ident in (-1, '-1', '', None):
                # create a new ident (it must be a string)
                a_sentence.ident = str(self.ds.select_scalar('SELECT max(id)+1 FROM sentence'))
            if not a_sentence.ident:
                a_sentence.ident = "1"
            # save sentence
            a_sentence.ID = ctx.sentence.save(a_sentence)
            # save shallow
            if a_sentence.shallow is not None:
                self.save_annotations(a_sentence, ctx=ctx)
            # save readings
            for reading in a_sentence.readings:
                # Update sentenceID
                reading.sentenceID = a_sentence.ID
                self.save_reading(reading, ctx=ctx)
        else:
            # update sentence
            pass
        # Select sentence
        return a_sentence

    def deleteReading(self, readingID):
        # delete all DMRS link, node
        self.dmrs_link.delete('dmrsID IN (SELECT ID FROM dmrs WHERE readingID=?)', (readingID,))
        self.dmrs_node_sortinfo.delete('dmrs_nodeID IN (SELECT ID FROM dmrs_node WHERE dmrsID IN (SELECT ID from dmrs WHERE readingID=?))', (readingID,))

        self.dmrs_node.delete('dmrsID IN (SELECT ID FROM dmrs WHERE readingID=?)', (readingID,))
        # delete all DMRS
        self.dmrs.delete("readingID=?", (readingID,))
        # delete parse_raws
        self.parse_raw.delete("readingID=?", (readingID,))
        # delete readings
        self.reading.delete("ID=?", (readingID,))

    def updateReading(self, reading):
        raise NotImplementedError

    def save_reading(self, reading, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.save_reading(reading, ctx=ctx)
        # ctx is not None now
        reading.ID = ctx.reading.save(reading)
        # Save raw
        for raw in reading.raws:
            raw.readingID = reading.ID
            ctx.parse_raw.save(raw)
        # Save DMRS
        for dmrs in reading.dmrs:
            dmrs.readingID = reading.ID
            dmrs.ID = ctx.dmrs.save(dmrs)
            # save nodes
            for node in dmrs.nodes:
                node.dmrsID = dmrs.ID
                # save realpred
                if node.rplemma:
                    # Escape lemma
                    lemma = self.lemmaCache.by_value(node.rplemma, ctx=ctx)
                    node.rplemmaID = lemma.ID
                # save gpred
                if node.gpred:
                    gpred_value = self.gpredCache.by_value(node.gpred, ctx=ctx)
                    node.gpred_valueID = gpred_value.ID
                # save sense
                if node.sense:
                    node.synsetid = node.sense.synsetid
                    node.synset_score = node.sense.score
                node.ID = ctx.node.save(node)
                # save sortinfo
                node.sortinfo.dmrs_nodeID = node.ID
                ctx.sortinfo.save(node.sortinfo)
            # save links
            for link in dmrs.links:
                link.dmrsID = dmrs.ID
                link.fromNodeID = link.fromNode.ID
                link.toNodeID = link.toNode.ID
                if link.rargname is None:
                    link.rargname = ''
                ctx.link.save(link)

    def build_search_result(self, rows, no_more_query=False):
        if rows:
            logger.debug(("Found: %s presentation(s)" % len(rows)))
        else:
            logger.debug("None was found!")
            return []
        sentences = []
        sentences_by_id = {}
        for row in rows:
            readingID = row['readingID']
            sentenceID = row['sentenceID']
            sentence_ident = row['sentence_ident']
            corpus = row['corpus']
            text = row['text']
            documentID = row['documentID']
            if sentenceID in sentences_by_id:
                # update reading
                a_reading = Reading(ID=readingID)
                # self.get_reading(a_reading)
                sentences_by_id[sentenceID].readings.append(a_reading)
            else:
                if no_more_query:
                    a_sentence = Sentence(ident=sentence_ident, text=text, documentID=documentID)
                    a_sentence.corpus = corpus
                    a_sentence.ID = sentenceID
                else:
                    a_sentence = self.getSentence(sentenceID, readingIDs=[], skip_details=True)
                a_sentence.readings = []
                a_reading = Reading(ID=readingID)
                a_sentence.readings.append(a_reading)
                sentences.append(a_sentence)
                sentences_by_id[sentenceID] = a_sentence
            # sentences.append(a_sentence)
        logger.debug(("Sentence count: %s" % len(sentences)))
        return sentences

    def get_reading(self, a_reading, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.get_reading(a_reading, ctx=ctx)
        # retrieve all DMRSes
        a_reading.dmrs = ctx.dmrs.select('readingID=?', (a_reading.ID,))
        for a_dmrs in a_reading.dmrs:
            # retrieve all nodes
            a_dmrs.nodes = ctx.node.select('dmrsID=?', (a_dmrs.ID,))
            for a_node in a_dmrs.nodes:
                # retrieve sortinfo
                list_sortinfo = ctx.sortinfo.select('dmrs_nodeID=?', (a_node.ID,))
                if len(list_sortinfo) == 1:
                    a_node.sortinfo = list_sortinfo[0]
                # retrieve realpred
                if a_node.rplemmaID:
                    a_node.rplemma = self.lemmaCache.by_id(int(a_node.rplemmaID), ctx=ctx).lemma
                # retrieve gpred
                if a_node.gpred_valueID:
                    a_node.gpred = self.gpredCache.by_id(int(a_node.gpred_valueID), ctx=ctx).value
                # create sense object
                if a_node.synsetid:
                    sense_info = Sense()
                    sense_info.synsetid = a_node.synsetid
                    sense_info.score = a_node.synset_score
                    sense_info.lemma = a_node.rplemma if a_node.rplemma else ''
                    sense_info.pos = a_node.synsetid[-1]
                    a_node.sense = sense_info
            # retrieve all links
            a_dmrs.links = ctx.link.select('dmrsID=?', (a_dmrs.ID,))
            # update link node
            for a_link in a_dmrs.links:
                a_link.fromNode = a_dmrs.getNodeById(a_link.fromNodeID, True)[0]
                a_link.toNode = a_dmrs.getNodeById(a_link.toNodeID, True)[0]
        return a_reading

    def saveParseRaw(self, a_raw, ctx=None):
        self.parse_raw.save(a_raw, ctx=ctx)

    def get_raw(self, readingID, reading=None, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.get_raw(readingID, reading, ctx=ctx)
        # ctx is not None
        raws = ctx.parse_raw.select('readingID=?', (readingID,))
        if reading is not None:
            for raw in raws:
                raw.readingID = reading.ID
                reading.raws.append(raw)
        return raws

    def getSentence(self, sentenceID, mode=None, readingIDs=None, skip_details=False, get_raw=True, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.getSentence(sentenceID, mode, readingIDs, skip_details, get_raw, ctx=ctx)
        # ctx was ensured
        a_sentence = ctx.sentence.by_id(sentenceID)
        if a_sentence is not None:
            self.get_annotations(sentenceID, a_sentence, ctx=ctx)
            # retrieve all readings
            conditions = 'sentenceID=?'
            params = [a_sentence.ID]
            if mode:
                conditions += ' AND mode=?'
                params.append(mode)
            if readingIDs and len(readingIDs) > 0:
                conditions += ' AND ID IN ({params_holder})'.format(params_holder=",".join((["?"] * len(readingIDs))))
                params.extend(readingIDs)
            a_sentence.readings = ctx.reading.select(conditions, params)
            for a_reading in a_sentence.readings:
                if get_raw:
                    self.get_raw(a_reading.ID, a_reading, ctx=ctx)
                if not skip_details:
                    self.get_reading(a_reading, ctx=ctx)
        else:
            logging.debug("No sentence with ID={} was found".format(sentenceID))
        # Return
        return a_sentence

    def delete_sent(self, sentenceID):
        # delete all reading
        sent = self.getSentence(sentenceID, skip_details=True, get_raw=False)
        # delete readings
        if sent is not None:
            for i in sent:
                self.deleteReading(i.ID)
        # delete words, concepts, cwl
        self.word.delete('sid=?', (sentenceID,))
        self.cwl.delete('cid IN (SELECT cid FROM concept WHERE sid=?)', (sentenceID,))
        self.concept.delete('sid=?', (sentenceID,))
        # delete sentence obj
        self.sentence.delete("ID=?", (sentenceID,))

    def get_annotations(self, sentenceID, sent_obj=None, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.get_annotations(sentenceID, sent_obj, ctx=ctx)
        # ctx is not None now
        if sent_obj is None:
            sent_obj = self.getSentence(sentenceID, skip_details=True, get_raw=False, ctx=ctx)
        # select words
        # select concepts
        sent_obj.words = ctx.word.select("sid=?", (sentenceID,))
        wmap = {w.ID: w for w in sent_obj.words}
        sent_obj.concepts = ctx.concept.select("sid=?", (sentenceID,))
        cmap = {c.ID: c for c in sent_obj.concepts}
        # link concept-word
        links = ctx.cwl.select("cid IN (SELECT ID from concept WHERE sid=?)", (sentenceID,))
        for lnk in links:
            cmap[lnk.cid].words.append(wmap[lnk.wid])
        # return annotation
        return sent_obj

    def save_annotations(self, sent_obj, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.save_annotations(sent_obj, ctx=ctx)
        # ctx is not None now ...
        for word in sent_obj.words:
            word.sid = sent_obj.ID
            word.ID = ctx.word.save(word)
        for concept in sent_obj.concepts:
            concept.sid = sent_obj.ID
            concept.ID = ctx.concept.save(concept)
            for word in concept.words:
                # save links
                logger.debug("Saving", CWLink(wid=word.ID, cid=concept.ID))
                ctx.cwl.save(CWLink(wid=word.ID, cid=concept.ID))
                pass

    def flag_sent(self, sid, flag, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.flag_sent(sid, flag, ctx=ctx)
        # update flag
        return ctx.sentence.update(new_values=(flag,), where='ID=?', where_values=(sid,), columns=('flag',))

    def next_sentid(self, sid, flag=None, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.next_sentid(sid, flag, ctx=ctx)
        sent_obj = ctx.sentence.by_id(sid, columns=('ID', 'documentID'))
        docid = sent_obj.documentID
        where = 'ID > ? AND documentID == ?'
        params = [sid, docid]
        if flag is not None:
            where += " AND flag = ?"
            params.append(flag)
        next_sent = ctx.sentence.select_single(where=where, values=params, orderby="documentID, ID", limit=1)
        return next_sent.ID if next_sent is not None else None

    def prev_sentid(self, sid, flag=None, ctx=None):
        if ctx is None:
            with self.ctx() as ctx:
                return self.prev_sentid(sid, flag, ctx=ctx)
        sent_obj = ctx.sentence.by_id(sid, columns=('ID', 'documentID'))
        docid = sent_obj.documentID
        where = 'ID < ? AND documentID == ?'
        params = [sid, docid]
        if flag is not None:
            where += " AND flag = ?"
            params.append(flag)
        prev_sent = ctx.sentence.select_single(where=where, values=params, orderby="documentID DESC, ID DESC", limit=1)
        return prev_sent.ID if prev_sent is not None else None
