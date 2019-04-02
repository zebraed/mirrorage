#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : __init__.py
# Copyright (c) 2019/ author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from future_builtins import map
from future_builtins import filter

import sys
import os

def reload():
    for k in sys.modules.keys():
        if k.find('psychoid') > -1:
            del sys.modules[k]
