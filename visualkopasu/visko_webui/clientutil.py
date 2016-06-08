'''
Django settings for VisualKopasu project.
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
__copyright__ = "Copyright 2013, Visual Kopasu"
__credits__ = [ "Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying" ]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

class DMRSNodeTooltip:
    def __init__(self, rows, cols):
        self.contents = [None] * rows
        for i in range(rows):
            self.contents[i] = [''] * cols
        self.rows = rows
        self.cols = cols
        self.max_id = rows * cols
        self.current_id = 0
    
    def push(self, info):
        if self.current_id < self.max_id:
            row_id = self.current_id // self.cols
            col_id = self.current_id % self.cols
            self.set_value(row_id, col_id, info)
            self.current_id += 1
    
    def set_value(self, row_id, col_id, info):
        self.contents[row_id][col_id]=info
    
    def str(self):
        count = 0
        js_content = "["
        for row in self.contents:
            row_content = "["
            for cell in row:
                count += 1
                if count > self.current_id:
                    break 
                if len(row_content) > 1:
                    row_content += ","
                row_content += "'%s'" % cell
            row_content += "]"
            if len(row_content) > 2:
                if len(js_content) > 1:
                    js_content += ", "
                js_content += row_content
        js_content += "]"
        return js_content
    
class DataUtil:
    @staticmethod
    def notEmpty(data):
        return data != None and len(data) > 0 
    
    @staticmethod
    def translate(item, a_dict = None):
        if a_dict == None:
            return item
        elif item in a_dict:
            return a_dict[item]
        else:
            return item
    
