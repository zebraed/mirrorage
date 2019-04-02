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

        userDefAttrDic = OrderedDict()
        if allUser:
            userAttrs = pm.listAttr(node, ud=1)
            print( '### ' + node + ' ###' )
            for ua in userAttrs:
                userDefAttrDic[ua] = cls.getAttrDict(node, ua)
        return userDefAttrDic

    @classmethod
    def getAttrDict(cls, node, at,  *args, **kwargs):
        """Get attribute params and shaping to dictonary.
        """
        node = getPy(node)

        attrDic = OrderedDict()
        attrDic["ln"] = node.attr(at).attrName(longName=1)

        if pm.attributeQuery(node.attr(at).name().split(".")[1], n=node.name(), sn=True) != None:
            attrDic["sn"] = pm.attributeQuery(node.attr(at).name().split(".")[1], n=node.name(), sn=True)
        
        if pm.attributeQuery(node.attr(at).name().split(".")[1], n=node.name(), nn=True) != None:
            attrDic["nn"] = pm.attributeQuery(node.attr(at).name().split(".")[1], n=node.name(), nn=True)


        attrDic["type"] = node.attr(at).type()

        if node.attr(at).isKeyable():
            attrDic["k"] = 1
        else:
            attrDic["k"] = 0
        
        if node.attr(at).isInChannelBox():
            attrDic["cb"] = 1
        else:
            attrDic["cb"] = 0

        if node.attr(at).isLocked():
            attrDic['l'] = 1
        else:
            attrDic['l'] = 0

        if node.attr(at).type() == "string":
            attrDic["attrflag"] = "dt"
        else:
            attrDic["attrflag"] = "at"

        if isNumericAttr(node.attr(at).type()):
            if node.attr(at).getMin() != None:
                attrDic["min"] = node.attr(at).getMin()
            if node.attr(at).getMax() != None:
                attrDic["max"] = node.attr(at).getMax()
            defaultVal    = pm.attributeQuery(node.attr(at).name().split(".")[1] , n=node.attr(at).name() , listDefault=1)
            attrDic["dv"] = get1st(defaultVal, default=0)

        if node.attr(at).type() == "enum":
            attrDic["enum"] = ":".join(node.attr(at).getEnums().keys())
                
        attrDic['value'] = cmds.getAttr(node.name()+ '.' + at)
        print(' export attribute... : ' + at)
        return attrDic
    
    @classmethod
    def exportAttrsToJson(cls, dictonary, **kwargs):
        """Convert and export attributes json file from dictonary data.
        """
        return json.dumps(dictonary, sort_keys=True, indent=4)

    @classmethod
    def importJsonToAttrs(cls, path, **kwargs):
        """import json file and decode orderDict.
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
    def setAddAttrs(cls, attributeDicts, node, _set=True, add=True, value=True, *args, **kwargs):
        """Set & add attrs from attribute dictonary member.
        """

        def _addDictAttr(node, value, attrflag, k, ln, _type, sn , nn, cb, **kwargs):
            _max   = getFlag(kwargs, ['maxVale', '_max'],    None)
            _min   = getFlag(kwargs, ['minValue', '_min'],   None)
            dv     = getFlag(kwargs, ['defaultValue', 'dv'], None)
            enum   = getFlag(kwargs, ['_enumerate', 'enum'], None)

            attrName = ln
            
            if attrflag == 'at':
                if isNumericAttr(_type):
                    pm.addAttr(node,
                            ln  = ln,
                            at  = _type,
                            dv  = dv,
                            k   = k,
                            min = _min,
                            max = _max,
                            sn  = sn,
                            nn  = nn,
                            )
                
                elif _type == 'enum':
                    pm.addAttr(node,
                            ln   = ln,
                            at   = _type,
                            en   = enum,
                            k    = k,
                            sn   = sn,
                            nn   = nn,
                            )
                else:
                    pm.addAttr(node,
                            ln  = ln,
                            at  = _type,
                            k   = k,
                            sn  = sn,
                            nn  = nn,
                            )

            elif attrflag == 'dt':
                pm.addAttr(node,
                        ln = ln,
                        dt = _type,
                        k  = k,
                        sn = sn,
                        nn = nn,
                        )
            if value:
                pm.setAttr(node.name() + '.' + attrName,
                        value
                        )
            if not k:
                if cb:
                    pm.setAttr(node.name() + '.' + attrName,
                            cb=cb
                            )

        def _setDictAttr(node, value, cb, k, ln, l, **kwargs):

            nodeAt = node.name() + '.' + ln

            pm.setAttr(nodeAt, value,
                    cb  = cb,
                    k   = k,
                    l   = l,
                    )

        node = getPy(node)
        s = attributeDicts

        attrNames = [ an for an in s.keys() ]

        for attrName in attrNames:
            attrsDict = s[attrName]

            value     = attrsDict['value']

            attrflag  = attrsDict['attrflag']

            k         = attrsDict['k']

            l         = attrsDict['l']

            cb        = attrsDict['cb']

            ln        = attrsDict['ln']

            _type     = attrsDict['type']

            try:
                sn    = attrsDict['sn']
            except:
                sn    = ln

            try:
                nn    = attrsDict['nn']
            except:
                nn    = sn
            
            try:
                enum  = attrsDict['enum']
            except:
                enum  = None

            if isNumericAttr(_type):
                _max  = attrsDict['max']

                _min  = attrsDict['min']

                dv    = attrsDict['dv']

            if add:
                if attrflag == 'at':
                    if isNumericAttr(_type):
                        _addDictAttr(node,
                                    value    = value,
                                    ln       = ln,
                                    attrflag = attrflag,
                                    dv       = dv,
                                    k        = k,
                                    _min     = _min,
                                    _max     = _max,
                                    _type    = _type,
                                    sn       = sn,
                                    nn       = nn,
                                    cb       = cb,
                                    )
                    elif enum:
                        _addDictAttr(node,
                                    value    = value,
                                    ln       = ln,
                                    attrflag = attrflag,
                                    enum     = enum,
                                    k        = k,
                                    _type    = _type,
                                    sn       = sn,
                                    nn       = nn,
                                    cb       = cb,
                                    )
                    else:
                        _addDictAttr(node,
                                    value    = value,
                                    ln       = ln,
                                    attrflag = attrflag,
                                    k        = k,
                                    _type    = _type,
                                    sn       = sn,
                                    nn       = nn,
                                    cb       = cb,
                                    )

                elif attrflag == 'dt':
                    _addDictAttr(node,
                                value    = value,
                                ln       = ln,
                                attrflag = attrflag,
                                k        = k,
                                _type    = _type,
                                sn       = sn,
                                nn       = nn,
                                cb       = cb,
                                )

            if _set:
                _setDictAttr(node,
                            value    = value,
                            ln       = ln,
                            l        = l,
                            k        = k,
                            _type    = _type,
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