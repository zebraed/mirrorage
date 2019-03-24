#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : newOrder.py
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


from mirrorage.qtpy.Qt import QtCore, QtGui, QtWidgets
from .. import widget as widget
from .. import cmdModule as cmdModule
import mirrorage.tools.attribute.attribute
from mirrorage.tools import *


class MenuItems(object):
    
    def __init__(self, *args, **kwargs):
        super(MenuItems, self).__init__(*args, **kwargs)
        self.cmd = mirrorage.tools.attribute.attribute.AttributeModules()
        self.newOrder = NewOrderCmd()

    def createMenuCmd(self):
        """Create menu commands in channelBox.
        """

        cbMenu   = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|menu2'
        editMenu = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|menu3'
        cbPopup  = 'ChannelBoxLayerEditor|MainChannelsLayersLayout|ChannelsLayersPaneLayout|ChannelBoxForm|menuBarLayout1|frameLayout1|mainChannelBox|popupMenu1'
        mainModMenu = 'MayaWindow|mainModifyMenu'

        mel.eval('generateChannelMenu {} 0;'.format(cbMenu))
        mel.eval('generateCBEditMenu  {} 0;'.format(editMenu))
        mel.eval('generateChannelMenu {} 1;'.format(cbPopup))
        mel.eval('ModObjectsMenu {};'.format(mainModMenu))

        channels_menuitems = [
            {'name': 'cb_menuDivider', 'label': '',                       'command': None},
            {'name': 'unlock_trs',     'label': 'Unlock Transformations', 'command': self.cmd.unlockAttrs},
        ]

        edit_menuitems = [
            {'name': 'opt_menuDivider',  'label': '',                     'command': None},
            {'name': 'add_divider',      'label': 'Add Divider',          'command': self.cmd.addDivider},
            {'name': 'sort_menuDivider', 'label': 'Sort Attributes',      'command': None},
            {'name': 'cbf_attrMoveUp',   'label': 'Move Attributes Up',   'command': self.cmd.moveUpAttr},
            {'name': 'cbf_attrMoveDown', 'label': 'Move Attributes Down', 'command': self.cmd.moveDownAttr},
            {'name': 'edit_menuDivider', 'label': '',                     'command': None},
            {'name': 'cbf_attrCut',      'label': 'Cut Attributes',       'command': self.newOrder.cutAttribute},
            {'name': 'cbf_attrCopy',     'label': 'Copy Attributes',      'command': self.newOrder.copyAttribute},
            {'name': 'cbf_attrPaste',    'label': 'Paste Attributes',     'command': self.newOrder.pasteAttr},
        ]

        self.removeItem(['divider'])
        self.removeItem([item['name'] for item in edit_menuitems])

        self.addCmdToMenu(channels_menuitems, cbMenu)
        self.addCmdToMenu(edit_menuitems, editMenu)
        self.addCmdToMenu(channels_menuitems, cbPopup)
        self.addCmdToMenu(edit_menuitems, cbPopup)
        self.addCmdToMenu(edit_menuitems, mainModMenu)

    def removeItem(self, nameList):
        for name in nameList:
            for item in pm.lsUI():
                if item.endswith(name):
                    pm.deleteUI(item)
    
    def addCmdToMenu(self, commands, menu):
        for item in commands:
            name    = item['name']
            label   = item['label']
            command = item['command']

            if '_menuDivider' in name:
                name = '{}_{}'.format(getLast(menu.split('|')), name)
                pm.menuItem(name, parent=menu, divider=True, dividerLabel=label)
            else:
                name = '{}_{}'.format(getLast(menu.split('|')), name)
                pm.menuItem(name, parent=menu, label=label, command=command)


class NewOrderCmd(cmdModule.CmdModule):

    def __init__(self, *args, **kwargs):
        super(NewOrderCmd, self).__init__(*args, **kwargs)
        self.cmd = mirrorage.tools.attribute.attribute.AttributeModules()
        self.copyData = None
        self.copyMode = None
    
    def copyAttribute(self, *args):
        self.saveSelAttrs('copy')
    
    def cutAttribute(self, *args):
        self.saveSelAttrs('cut')

    def saveSelAttrs(self, mode, **kwargs):
        if not pm.selected():
            pm.displayWarning('please select object.')
            return
        
        srcItem = getLast(pm.selected())
        allSelAttr = self.cmd.getSelectedAttrs()

        if not allSelAttr:
            pn.displayWarning('No attribute selected.')
            return
        
        allUserAttrs = self.cmd.getAllUserAttrs(srcItem)
        udAttr = [ attr for attr in allSelAttr if attr in allUserAttrs ]
        if not udAttr:
            pm.displayWarning('No user difined attributes selected.')
            return
        
        self.copyData = {'sourceItem':srcItem, 'attribute':udAttr}
        self.copyMode = mode
    
    def pasteAttr(self, *args):
        if not getLast(pm.selected()):
            pm.displayWarning('please select object.')
            return
        tarItem  = getLast(pm.selected())
        srcItem  = self.copyData['sourceItem']
        moveAttr = self.copyMode == 'cut'
        for attr in self.copyData['attribute']:
            self.cmd.copyAttr(srcItem, tarItem, attr, move=moveAttr)
        
        pm.select(tarItem)
    
    def execute(self, *args):
        mi = MenuItems()
        mi.createMenuCmd()


'''
import mirrorage.tools.attribute.newOrder as no
reload( mirrorage.tools.attribute.newOrder)
import mirrorage.tools.attribute.attribute
reload( mirrorage.tools.attribute.attribute)

a = no.NewOrderCmd()
a.execute()
'''