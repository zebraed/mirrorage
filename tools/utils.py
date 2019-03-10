#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : utils.py
# Copyright (c) 2019 / author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import print_function
#from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future_builtins import map
from future_builtins import filter

import pymel.core as pm


def getFlag(kwargs, args_list, default_value):
    """
    multiple argument.

    Args:
        kwargs(dict): keyword argument
        arg_list(list or tuple or string): 

    Returns:
        argument value, default_value if not
    
    ex.)
        name = getFlag(kwargs, ['name', 'n'], 'node#')
    """
    if not isinstance(args_list, (list, tuple)):
        args_list = [args_list]

    for ag in args_list:
        if ag in kwargs.keys():
            return kwargs[ag]
    return default_value