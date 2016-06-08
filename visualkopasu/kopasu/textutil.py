'''
Data access layer for VisualKopasu project.
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

import sys

if sys.version_info >= (3,0):

    class EncodingUtil:
        @staticmethod
        def to_unicode(obj):
            return obj

else:
    class EncodingUtil:
        @staticmethod
        def to_unicode(obj):
            if isinstance(obj, basestring) and (not isinstance(obj, unicode)):
                obj = unicode(obj, 'utf-8')
            return obj
