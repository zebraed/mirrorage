#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : __init__.py
# Copyright (c) 2019/ author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future_builtins import map
from future_builtins import filter

import pymel.core as pm

try:
    unicode
except:
    unicode = str


def getPy(args):
    """this is convertion pymel object from string or unicode argument.

    Args:
    :param arg : (string or unicode) argument.
    :return    : (pymel object) or throw.
    """
    if isinstance(arg, (str, unicode)):
        return pm.PyNode(arg)
    else:
        return arg