"""
Global config file for VisualKopasu
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

import os
from texttaglib.chirptext import AppConfig

# Fall back to this project root if necessary
DEFAULT_ROOT = os.path.expanduser('~/local/visko/')

# try to read from django setting
try:
    from django.conf import settings
    _PROJECT_ROOT = getattr(settings, "VISKO_ROOT", DEFAULT_ROOT)
except Exception:
    # try to reaf from config file
    cfg = AppConfig("visko", mode=AppConfig.JSON)
    if cfg.config and "VISKO_ROOT" in cfg.config:
        _PROJECT_ROOT = cfg.config["VISKO_ROOT"]
    else:
        _PROJECT_ROOT = DEFAULT_ROOT


class ViskoConfig:
    PROJECT_ROOT = _PROJECT_ROOT
    DATA_FOLDER = os.path.join(PROJECT_ROOT, 'data')
    BIBLIOTECHE_ROOT = os.path.join(DATA_FOLDER, 'biblioteche')
