#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : menuItems.py
# Copyright (c) 2019 / author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future_builtins import map
from future_builtins import filter

import pymel.core as pm
from maya import cmds
from maya import mel

import os
import sys
from collections import OrderedDict
from functools import partial

MENU_NAME = ""

class MenuItems(object):
    """Base class for create and add menu items in channelBox attribute menu.
    """
    maya_ver = int(cmds.about(v=1)[:4])

    def __init__(self):
        #self._remove()
        pass
    
    def _remove(self):
        """
        Checks if there is a marking menu with the given name and if so deletes it to
        prepare fot creating a new one. We do this in order to be able to easily update our making munus.
        """
        if pm.popupMenu(MENU_NAME, ex=1):
            pm.deleteUI(MENU_NAME)
    
    def addCmdToMenu(self, commands, menu):
        for item in commands:
            name    = item['name']
            label   = item['label']
            command = item['command']

            name = '{}_{}'.format(getLast(menu.split('|')), name)
            pm.menuItem(name, parent=menu, label=label, command=command)

    def createMenuCmd(self, *args, **kwargs):
        """Create menu commands in channelBox.
        e.g.)
        marking_menuitems = [
            {'name': 'marking', 'label': '',                  'command': None},
            {'name': name,     'label': label_name, 'radialPosition': rp ,'command': command},
        ]

        ...

        edit_menuitems = [
            {'name': 'opt_menuDivider',  'label': '',                      'command': None},
            {'name': 'add_divider',      'label': 'Add Division',          'command': self.cmd.addDivision},
        ]
        """
        pass