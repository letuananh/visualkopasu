'''
Global config file for VisualKopasu
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

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2012, Visual Kopasu"
__credits__ = ["Fan Zhenzhen", "Francis Bond", "Le Tuan Anh", "Mathieu Morey", "Sun Ying"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

import os


class ViskoConfig:
    PROJECT_ROOT = os.path.expanduser('~/workspace/visualkopasu')
    DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data')
    BIBLIOTECHE_ROOT = os.path.join(DATA_FOLDER, 'biblioteche')

    # Django database - DO NOT CHANGE THIS!
    DATABASES_default_ENGINE = 'django.db.backends.sqlite3'
    DATABASES_default_NAME = os.path.join(PROJECT_ROOT, 'data/visko.db')
