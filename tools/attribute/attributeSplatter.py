#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : attributeSplatter.py
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

import os
import sys
from collections import OrderedDict

import json

from psychoid.qtpy.Qt import QtCore, QtGui, QtWidgets
from .. import widget as widget
from psychoid.tools import *
import psychoid.modules.attribute as att
att = att.AttributeModules


try:
    unicode
except:
    unicode = str
    
class cmd(object):
    """ private method
    """
    
    @classmethod
    def exportUserDefineAttribute(cls, node='', at='',  *args, **kwargs):
        """Export user defined attributes.
        """
        if node == '':
            node = get1st(pm.selected())
        if at == '':
            allUser = True
        node = getPy(node)

        userDefAttrDic = OrderedDict()
        if allUser:
            userAttrs = pm.listAttr(node, ud=1)
            print( '### ' + node + ' ###' )
            for ua in userAttrs:
                userDefAttrDic[ua] = att.getAttrDict(node.attr(ua))
        return userDefAttrDic
    
    @classmethod
    def exportAttrsToJson(cls, dictonary, **kwargs):
        """Convert and export attributes json file from dictonary data.
        """
        return json.dumps(dictonary, sort_keys=True, indent=4)

    @classmethod
    def importJsonToAttrs(cls, path, **kwargs):
        """import json file and decode orderedDict.
        """
        f = open(path, 'r')
        s = f.read()
        #Keep order keys and values.
        deco   = json.JSONDecoder(object_pairs_hook=OrderedDict)
        atDict = deco.decode(s)
        f.close()
        return atDict

    @classmethod
    def exportFile(cls, *args, **kwargs):
        """Utility func by file exporter.
        """
        directory = getFlag(kwargs, ['directory', 'd'], "")
        auto      = getFlag(kwargs, ['autoName', 'auto'], False)
        extension = getFlag(kwargs, ['extension', 'ext'], ".json")

        for arg in args:
            if extension in directory:
                directory = directory.replace(extension, '')
            if auto:
                fp = directory  + 'jsonFile' + extension
            else:
                fp = directory + extension
            try:
                fw = open(fp,'w')
            except:
                raise
            fw.write(arg)
            print('# > export attribute settings file : ' + os.path.join(directory, fp))
            print('# Done!')
            fw.close()

    @classmethod
    def setAddAttrs(cls, attributeDicts, node, _set=True, add=True, *args, **kwargs):
        """Set & add attrs from attribute dictonary member.
        """
        node = getPy(node)
        for k in attributeDicts.keys():
            if add:
                attributeDicts = convert_keys_to_string(attributeDicts)
                attrName = attributeDicts[k]['ln']
                pm.addAttr(node, **attributeDicts[attrName])

            if _set:
                if attributeDicts[k]['hidden']:
                    cb = 0
                else:
                    cb = 1

                if attributeDicts[k]['keyable']:
                    k = 1
                    l = 0
                else:
                    k = 0
                    l = 1

                pm.setAttr(node.attr(attributeDicts[k]['ln']),
                            l        = l,
                            k        = k,
                            cb       = cb,
                            )


class AttributeSplatterGUI(widget.CustomMoveAnimationWidget):
    title = "Attribute Splatter"
    windowName = 'attributeSplatterWidget'

    def __init__(self, *args, **kwargs):
        return super(AttributeSplatterGUI, self).__init__(*args, **kwargs)
        self.cmd = cmd()

    def setLayout(self, mainWidget):
        #self.resize(300, 140)
        
        self.mainVL = QtWidgets.QVBoxLayout()
        #self.addHelpDoc(os.getcwd())
        #widget.Image(r'')
        self.mainVL.addWidget(QtWidgets.QLabel("Attribute Splatter"), alignment=QtCore.Qt.AlignCenter)
        sp = widget.separator()
        self.mainVL.addWidget(sp)

        #mainVL.addWidget(QtWidgets.QLabel)

        HV   = QtWidgets.QHBoxLayout()
        exPB = QtWidgets.QPushButton('Export')
        exPB.clicked.connect(self.getSavePath)
        imPB = QtWidgets.QPushButton('Import')
        imPB.clicked.connect(self.getOpenPath)

        #rclic = RightClickButton()

        HV.addWidget(exPB)
        HV.addWidget(imPB)

        self.psL, self.psLE = widget.textFieldButtonGrp(l='Set Node :', bl='set', cwl='90')

        self.userOnly = QtWidgets.QCheckBox('Export only user defined attribute', checked=1)
        self.mainVL.addWidget(self.userOnly)
        self.mainVL.addLayout(self.psL)
        self.mainVL.addLayout(HV)

        self.mainVL.addStretch()

        mainWidget.setLayout(self.mainVL)

    def getOpenPath(self):
        self.getNode()
        self.openPath = widget.fileDialog(self, mode='open')
        if not self.openPath:
            return
        self.openJsonFile(self.openPath)

    def getSavePath(self):
        self.getNode()
        self.savePath = widget.fileDialog(self, mode='save')
        if not self.savePath:
            return
        self.saveJsonFile(self.savePath)
    
    def saveJsonFile(self, path):
        j_file = cmd.exportAttrsToJson(self.atDict)
        cmd.exportFile(j_file, d=path)

    def openJsonFile(self, paht):
        attrsDict = cmd.importJsonToAttrs(self.openPath)
        self.setAdd(attrsDict)
    
    def getNode(self):
        self.atDict = cmd.exportUserDefineAttribute(node=self.psLE.text())

    @widget.undo
    def setAdd(self, attrsDict, **kwargs):
        cmd.setAddAttrs(attributeDicts=attrsDict ,node=self.psLE.text())