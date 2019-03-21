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

import re

import pymel.core as pm

try:
    unicode
except:
    unicode = str


def getPy(arg):
    """Convert to pymel object from string or unicode argument.

    Args:
    :param arg : (string or unicode) argument.
    :return    : (pymel object) or throw.
    """
    if isinstance(arg, (str, unicode)):
        return pm.PyNode(arg)
    else:
        return arg


def getFlag(kwargs, args_list, default_value):
    """
    multiple argument.

    Args:
        kwargs(dict): keyword argument
        arg_list(list or tuple or string):

    Returns:
        argument value, default_value if not
    
    e.g.)
        name = getFlag(kwargs, ['name', 'n'], 'node#')
    """
    if not isinstance(args_list, (list, tuple)):
        args_list = [args_list]

    for ag in args_list:
        if ag in kwargs.keys():
            return kwargs[ag]
    return default_value


def get1st(value, default=None, **kwargs):
    """this is Return 1st item of the given value.

    Parameters
    ----------
    value : mixed
        the value to operate.

    default : mixed
        default result if the value was None. (defult : None)
    
    string : bool
        as string char.


    Returns
    -------
        mixed
    
    """
    string = getFlag(kwargs, ['string', 's'], False)
    if hasattr(value, '__iter__'):
        try:
            return value[0]
        except:
            return default
    else:
        if string:
            if isinstance(value, (str, unicode)):
                return value[0]
        else:
            return value


def getLast(value, default=None, **kwargs):
    """this is Return Last list item value.

    Parameters
    ----------
    value : mixed
        the value to operate.

    default : mixed
        default result if the value was None. (defult : None)
    
    string : bool
        as string char.


    Returns
    -------
        mixed    
    """
    string = getFlag(kwargs, ['string', 's'], False)
    if hasattr(value, '__iter__'):
        try:
            return value[-1]
        except:
            return default
    else:
        if string:
            if isinstance(value, (str, unicode)):
                return value[-1]
        else:
            return value


def solveNodeName( nameLst, node="", **kwargs):
    """Rename node name by according to certain naming regulations.

    Parameters
    ----------
    nameList : [string]
        -

    node     : obj or str 
        -

    Returns
    -------
        mixed
    
    e.g.)
        solveNodeName(['cone', '~', 'L'], node='pCone1_cube_C')
        # Result: 'cone_cube_L' #
    """
    newName = []
    nodeLst = []
    if node != "":
        nodeLst  = node.split('_')
    flg = 1
    for i, n in enumerate(nameLst):
        if n.find("~") > -1:
            if len(nodeLst) > i:
                n = n.replace('~', nodeLst[i])
            else:
                flg = -1
        if n.find("=") > -1:
            n = n.replace('=', pm.PyNode(node).type())

        matchList = re.findall( '\[(.+?)\]', n)
        if matchList != None:
            for m in matchList:
                n = n.replace( '[%s]'%m, m[0].upper()+m[1:])

        if flg > 0:
            newName.append( n )
        flg = 1
    return '_'.join(newName)


def isNumericAttr(_type):
    """check isNumericAttr.
    """
    isNumericAttr = 0
    numAttrs = ['long', 'short', 'byte', 'float', 'double', 'doubleAngle', 'doubleLiner', 'time']
    for numAttr in numAttrs:
        if numAttrs == _type:
            return True
        else:
            return False