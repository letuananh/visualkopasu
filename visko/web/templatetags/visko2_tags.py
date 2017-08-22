# -*- coding: utf-8 -*-

'''
Visko 2.0's tags
@author: Le Tuan Anh
'''

# Copyright 2017, Le Tuan Anh (tuananh.ke@gmail.com)
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
# along with VisualKopasu. If not, see http://www.gnu.org/licenses/

__author__ = "Le Tuan Anh"
__copyright__ = "Copyright 2017, Visual Kopasu"
__credits__ = ["Francis Bond"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Le Tuan Anh"
__email__ = "tuananh.ke@gmail.com"
__status__ = "Prototype"

########################################################################

from lxml import etree

########################################################################

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def pretty_xml(value):
    return etree.tostring(etree.XML(value), pretty_print=True, encoding='utf-8')


@register.filter
def multilines(value):
    return mark_safe(value.replace('\n', '<br/>'))
