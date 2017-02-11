'''
A lite-weight ORM library
@author: Le Tuan Anh
'''

# Copyright 2012, Le Tuan Anh (tuananh.ke@gmail.com)
# This file is part of ChibiORM.
# ChibiORM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# ChibiORM is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with VisualKopasu. If not, see http://www.gnu.org/licenses/.

########################################################################

import logging
import copy
import sqlite3

########################################################################

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2013"
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################


class ORMInfo:
    def __init__(self, table_name, mapping, prototype, columnID='ID', orm_manager=None):
        self.table_name = table_name
        self.mapping = mapping
        self.prototype = prototype
        self.columnID = columnID
        self.orm_manager = orm_manager
        if(not orm_manager):
            logging.debug("There is no ORM manager for table %s" % table_name)

    def create_instance(self):
        return copy.deepcopy(self.prototype)

    def getByID(self, id, updateTo=None):
        if self.orm_manager:
            return self.orm_manager.selectRecordByID(self,id, updateTo)
        else:
            return None

    def select(self, condition='', args=[], fillTo=None):
        return self.orm_manager.selectRecords(self, condition, args, fillTo)

    def save(self, record, context=None, update_back=False):
        return self.orm_manager.store_record(self, record, context=context)


class DBContext():
    def __init__(self, conn=None, cur=None, auto_commit=False, auto_close=False):
        self.conn = conn
        self.cur = conn.cursor() if conn and cur is None else cur
        self.auto_commit = auto_commit
        self.auto_close = auto_close

    '''
    Commit and clean
    '''
    def flush(self):
        try:
            self.conn.commit()
            LiteORM.clean(self.conn)
        except Exception as e:
            logging.debug("Error while committing changes: %s" % e)
            pass
        pass


class LiteORM():
    def __init__(self, db_path):
        self.db_path = db_path

    def getConnection(self):
        connection = sqlite3.connect(self.db_path)
        return connection

    '''
    Close connection after use
    '''
    @staticmethod
    def clean(conn):
        if conn:
            try:
                conn.close()
            except Exception as e:
                logging.debug("Error while closing %s" % e)
                pass
        pass    
    
    '''
    Execute an insert query
    '''
    def execute_insert(self, query, params):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            # execute query
            cur.execute(query, params)
            last_id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
            # commit changes
            conn.commit()
            return last_id
        except sqlite3.Error as e:
            logging.debug("Query: %s" % query)
            logging.debug("Params: %s" % params)
            logging.debug("Error happened while trying to store a record: %s" % e)
            pass
        finally:
            LiteORM.clean(conn)
        # otherwise, failed
        return None
    
    def selectScalar(self, query, params):
        try:
            conn = self.getConnection()
            cur = conn.cursor()
            # execute query
            value = cur.execute(query, params).fetchone()[0]
            return value
        except sqlite3.Error as e:
            pass
        finally:
            self.clean(conn)
        # otherwise, failed
        return None

    def selectRows(self, query, params):
        try:
            conn = self.getConnection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # execute query
            rows = cur.execute(query, params).fetchall()
            return rows
        except sqlite3.Error as e:
            logging.debug("DB ERROR: %s" % e)
            pass
        finally:
            self.clean(conn)
        # otherwise, failed
        return None

    '''
    Save a record to database
    '''
    def store_record(self, mapping_info, record, update_back=False, context=None):
        last_id = None
        conn = None
        query = None
        try:
            conn = context.conn if (context and context.conn) else self.getConnection()
            cur = context.cur if (context and context.cur) else conn.cursor()
            # execute query
            fields = []
            params = []
            for attribute in mapping_info.mapping:
                if type(attribute) == list:
                    fields.append(attribute[0])
                    params.append(record.__dict__[attribute[1]])
                else:
                    fields.append(attribute)
                    params.append(record.__dict__[attribute])

            query = 'INSERT INTO {table_name} ({fields}) VALUES ({args})'.format(
                    table_name=mapping_info.table_name,
                    fields=','.join(fields),
                    args=','.join(['?'] * len(fields)))

            logging.debug("Executing store_record: SQL = %s" % query)
            logging.debug("params = %s" % params)

            cur.execute(query, params)
            last_id = cur.execute('SELECT last_insert_rowid()').fetchone()[0]
            # TODO: Fix this!
            record.__dict__[mapping_info.columnID] = last_id
            # commit changes
            if (not context) or (context.auto_commit):
                conn.commit()
        except sqlite3.Error as e:
            logging.error("Error happened while trying to store a record: %s" % e)
            if query:
                logging.debug("Query: %s" % query)
                logging.debug("Params: %s" % params)
            pass
        finally:
            if (not context) or (context.auto_close):
                self.clean(conn)
        if update_back:
            self.selectRecordByID(mapping_info, last_id, record)
        return last_id    

    def selectRecords(self, mapping_info, condition = '', params = [], a_list = None):
        conn = None
        if condition:
            query = 'SELECT * FROM {table_name} WHERE {condition}'.format(
                            table_name = mapping_info.table_name
                            ,condition = condition)
        else:
            query = 'SELECT * FROM {table_name}'.format(
                            table_name = mapping_info.table_name)
        try:
            conn = self.getConnection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # execute query
            rows = cur.execute(query, params).fetchall()
            if a_list == None:
                a_list = []
            
            for row in rows:
                an_object = mapping_info.create_instance()
                an_object.update_fields(mapping_info.mapping, dict(row))                
                a_list.append(an_object)
        except sqlite3.Error as e:
            logging.debug("Error happened while selecting records: %s" % e)
            logging.debug("Current database file: %s" % self.db_path)
            pass
        finally:
            self.clean(conn)
        return a_list
    
    def selectRecord(self, query, params):
        try:
            conn = self.getConnection()
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            # execute query
            rows = cur.execute(query, params).fetchall()
            if len(rows) == 1:
                return dict(rows[0])
        except sqlite3.Error as e:
            logging.debug("Error happened while selectRecord: %s" % e)
            pass
        finally:
            self.clean(conn)
        # otherwise, failed
        return None
    
    def selectRecordByID(self, mapping_info, ID, an_object = None):
        query = 'SELECT * FROM {table_name} WHERE ID=?'.format(table_name=mapping_info.table_name)
        record_row = self.selectRecord(query, [ID])
        if record_row:
            if not an_object:
                an_object = mapping_info.create_instance()
            an_object.update_fields(mapping_info.mapping, record_row)
            return an_object
        else:
            return None

class SmartRecord:
    def __init__(self):
        pass
    
    def set_property(self, property, value):
        self.__dict__[property] = value
        return self
        
    def update_from(self, a_dict):
        for key in self.__dict__.keys():
            if key in a_dict:
                self.set_property(key, a_dict[key])
        return self
    
    def update_fields(self, map_info, a_dict):
        for pair in map_info:
            if type(pair) == list:
                # logging.debug("using list mode for %s" % pair)
                self.update_field(pair[1], pair[0], a_dict)
            elif type(pair) == str:
                self.update_field(pair, pair, a_dict)
            else:
                # TODO: error?
                pass
        return self
    
    def update_field(self, property_name, tag_attribute, a_dict):
        if not tag_attribute:
            tag_attribute = property_name
        if tag_attribute in a_dict:
            self.set_property(property_name, a_dict[tag_attribute])
        return self
            
    def __str__(self):
        return str(',\t '.join('%s : %s' % (k, str(v)) for (k, v) in self.__dict__.items() if v))
