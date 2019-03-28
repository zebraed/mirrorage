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



class MenuItems(object):
    """Base class for create and add menu items in channelBox attribute menu.
    """
    self.maya_ver = int(cmds.about(v=1)[:4])
    
    def __init__(self, *args, **kwargs):
        super(MenuItems, self).__init__(*args, **kwargs)

        if self.maya_ver > 2015:
            self.cbMenu   = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|menu2'
            self.editMenu = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|menu3'
            self.cbPopup  = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|frameLayout1|mainChannelBox|popupMenu1'
            self.mainModMenu = 'MayaWindow|mainModifyMenu'
        else:
            pass

        mel.eval('generateChannelMenu {} 0;'.format(self.cbMenu))
        mel.eval('generateCBEditMenu  {} 0;'.format(self.editMenu))
        mel.eval('generateChannelMenu {} 1;'.format(self.cbPopup))
        mel.eval('ModObjectsMenu {};'.format(self.mainModMenu))

    def removeItem(self, nameList):
        """Remove items from menuUI.
        """
        for name in nameList:
            for item in pm.lsUI():
                if item.endswith(name):
                    pm.deleteUI(item)
    
    def addCmdToMenu(self, commands, menu, dividerName='_menuDivider'):
        for item in commands:
            name    = item['name']
            label   = item['label']
            command = item['command']

            if dividerName in name:
                name = '{}_{}'.format(getLast(menu.split('|')), name)
                pm.menuItem(name, parent=menu, divider=True, dividerLabel=label)
            else:
                name = '{}_{}'.format(getLast(menu.split('|')), name)
                pm.menuItem(name, parent=menu, label=label, command=command)

    def createMenuCmd(self, *args, **kwargs):
        """Create menu commands in channelBox.
        e.g.)
        channels_menuitems = [
            {'name': 'cb_menuDivider', 'label': '',                  'command': None},
            {'name': name,     'label': label_name, 'command': command},
        ]

        edit_menuitems = [
            {'name': 'opt_menuDivider',  'label': '',                      'command': None},
            {'name': 'add_divider',      'label': 'Add Division',          'command': self.cmd.addDivision},
        ]
        """
        pass