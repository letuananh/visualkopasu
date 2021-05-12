#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper functions
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

import os
import logging
from lxml import etree


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def getSubFolders(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isdir(os.path.join(a_folder, child))]


def getFiles(a_folder):
    return [child for child in os.listdir(a_folder) if os.path.isfile(os.path.join(a_folder, child))]


def xml_to_str(xml_node, pretty_print=True):
    return etree.tostring(xml_node, pretty_print=True, encoding='utf-8').decode('utf-8')


class PaginationException(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Pagination(object):

    def __init__(self, index, total, from_idx, to_idx):
        """
        Pagination information
        """
        self.index = index
        self.total = total
        self.from_idx = from_idx
        self.to_idx = to_idx

    @property
    def is_first(self):
        return self.index <= 0

    @property
    def is_last(self):
        return self.index >= self.total - 1

    @property
    def left_pages(self):
        return range(self.from_idx, self.index)

    @property
    def previous(self):
        if self.is_first:
            return None
        else:
            return self.index - 1

    @property
    def next(self):
        if self.is_last:
            return None
        else:
            return self.index + 1

    @property
    def right_pages(self):
        return range(self.index + 1, self.to_idx)

    @property
    def pages(self):
        return range(self.from_idx, self.to_idx)

    def __str__(self):
        return "Pagination({}, {}, {}, {})".format(repr(self.index),
                                                   repr(self.total),
                                                   repr(self.from_idx),
                                                   repr(self.to_idx))


class Paginator(object):
    def __init__(self, pagesize=1000, windowpane=5):
        """
        """
        if pagesize is None or pagesize <= 0:
            raise PaginationException("Invalid page size (a positive integer is required) but {} was provided".format(repr(pagesize)))
        if windowpane is None or windowpane <= 0:
            raise PaginationException("Invalid windowpane size (a positive integer is required) but {} was provided".format(repr(windowpane)))
        # how many item per page
        self._pagesize = pagesize
        # Only show window pages left & right
        # E.g. window = 3 means:
        # -3 -2 -1 [current_page] 1 2 3
        self._windowpane = windowpane

    @property
    def pagesize(self):
        return self._pagesize

    @property
    def windowpane(self):
        return self._windowpane

    def total(self, item_count):
        if item_count is None or item_count < 0:
            raise PaginationException("Invalid item count ({} was provided".format(repr(item_count)))
        extra = 1 if item_count % self.pagesize else 0
        return item_count // self.pagesize + extra

    def paginate(self, page, total):
        if page is None or page < 0:
            raise PaginationException("Invalid page index")
        if total is None or total < 0:
            raise PaginationException("Invalid total page")
        if page < self.windowpane:
            left = 0
            extra = self.windowpane - page
            right = min(total, page + self.windowpane + extra + 1)
        elif page >= total - self.windowpane:
            right = total
            extra = self.windowpane - (total - page - 1)
            left = max(0, page - self.windowpane - extra)
        else:
            left = page - self.windowpane
            right = page + self.windowpane + 1
        return Pagination(page, total, left, right)
