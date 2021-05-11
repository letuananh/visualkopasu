"""
Global config file for VisualKopasu
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

import os


class ViskoConfig:
    PROJECT_ROOT = os.path.expanduser('~/local/visko/')
    DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data')
    BIBLIOTECHE_ROOT = os.path.join(DATA_FOLDER, 'biblioteche')

    # Django database - DO NOT CHANGE THIS!
    DATABASES_default_ENGINE = 'django.db.backends.sqlite3'
    DATABASES_default_NAME = os.path.join(PROJECT_ROOT, 'data/visko.db')
