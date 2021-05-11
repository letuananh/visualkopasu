# -*- coding: utf-8 -*-

"""
Visko 2.0's tags
@author: Le Tuan Anh
"""

# This code is a part of visualkopasu (visko): https://github.com/letuananh/visualkopasu
# :copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
# :license: GPLv3, see LICENSE for more details.

from lxml import etree

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def pretty_xml(value):
    return etree.tostring(etree.XML(value), pretty_print=True, encoding='utf-8')


@register.filter
def multilines(value):
    return mark_safe(value.replace('\n', '<br/>'))
