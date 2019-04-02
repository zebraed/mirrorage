#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : newOrder.py
# Copyright (c) 2019 / author : R.O a.k.a last_scene
# Thanks to jer.
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


from psychoid.qtpy.Qt import QtCore, QtGui, QtWidgets
from .. import widget as widget
import psychoid.modules as mod
import psychoid.modules.attribute as att
from psychoid.tools import *



class NewOrder(att.MenuItems):
    
    def __init__(self, *args, **kwargs):
        super(NewOrder, self).__init__(*args, **kwargs)

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

        self.cmd = att.AttributeModules()
        self.newOrder = NewOrderCmd()

    def _remove(self, nameList, **kwargs):
        """Remove items from menuUI.
           overwrite method.
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

    def createMenuCmd(self):
        """Create menu commands in channelBox.
        """
        channels_menuitems = [
            {'name': 'cb_menuDivider', 'label': '',                  'command': None},
            {'name': 'unlock_trs',     'label': 'Unlock Transforms', 'command': self.cmd.unlockAttrs},
        ]

        edit_menuitems = [
            {'name': 'opt_menuDivider',  'label': '',                      'command': None},
            {'name': 'add_divider',      'label': 'Add Division',          'command': self.cmd.addDivision},
            {'name': 'sort_menuDivider', 'label': 'Sort Attributes',       'command': None},
            {'name': 'cbf_attrMoveUp',   'label': 'Move Up',   'command': self.cmd.moveUpAttr},
            {'name': 'cbf_attrMoveDown', 'label': 'Move Down', 'command': self.cmd.moveDownAttr},
            {'name': 'edit_menuDivider', 'label': '',                      'command': None},
            {'name': 'cbf_attrCut',      'label': 'Cut Attr',              'command': self.newOrder.cutAttribute},
            {'name': 'cbf_attrCopy',     'label': 'Copy Attr',             'command': self.newOrder.copyAttribute},
            {'name': 'cbf_attrPaste',    'label': 'Paste Attr',            'command': self.newOrder.pasteAttr},
            {'name': 'export_menuDivider', 'label': '',                    'command': None},

        ]

        #init
        self._remove(['divider'])
        self._remove([item['name'] for item in edit_menuitems])
        self._remove([item['name'] for item in channels_menuitems])

        #add
        self.addCmdToMenu(channels_menuitems, self.cbMenu)
        self.addCmdToMenu(edit_menuitems, self.editMenu)
        self.addCmdToMenu(channels_menuitems, self.cbPopup)
        self.addCmdToMenu(edit_menuitems, self.cbPopup)
        self.addCmdToMenu(edit_menuitems, self.mainModMenu)


class NewOrderCmd(mod.CmdModule):

    def __init__(self, *args, **kwargs):
        super(NewOrderCmd, self).__init__(*args, **kwargs)
        self.cmd = att.AttributeModules()
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
        mi = NewOrder()
        mi.createMenuCmd()


'''
import psychoid.tools.attribute.newOrder as no
reload(no)
import psychoid.modules.attribute as att
reload(att)

a = no.NewOrderCmd()
a.execute()
'''