#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : attribute.py
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
from collections import Mapping
import itertools

from mirrorage.qtpy.Qt import QtCore, QtGui, QtWidgets
from .. import widget as widget
from .. import cmdModule as cmdModule

from mirrorage.tools import *

############################
# attribute utilitu module # 
############################


class AttributeModules(cmdModule.CmdModule):
    
    @classmethod
    def getAttrDict(cls, attribute):
        """Get attribute params and shaping to dictonary.
        """
        attribute_type = str(attribute.type())

        d_data = OrderedDict()
        d_data['ln'] = str(pm.attributeName(attribute, long=True))
        d_data['nn'] = str(pm.attributeName(attribute, nice=True))
        d_data['sn'] = str(pm.attributeName(attribute, short=True))
        d_data['hidden'] = attribute.isHidden()
        d_data['keyable'] = attribute.isKeyable()

        if attribute_type in ['string']:
            d_data['dataType'] = attribute_type
        else:
            d_data['attributeType'] = attribute_type

        if isNumericAttr(attribute_type):
            d_data['defaultValue'] = attribute.get(default=True)
            if attribute.getMax():
                d_data['maxValue'] = attribute.getMax()
            if attribute.getMin():
                d_data['minValue'] = attribute.getMin()

        if attribute_type in ['enum']:
            d_data['enumName'] = attribute.getEnums()

        if attribute.parent():
            d_data['parent'] = attribute.parent().attrName()

        return d_data
    
    @classmethod
    def copyAttr(cls, srcNode, tarNode, attrName, move=False, **kwargs):
        if isinstance(srcNode, str or unicode):
            srcNode = getPy(srcNode)
        
        if isinstance(tarNode, str or unicode):
            tarNode = getPy(tarNode)
        
        if not srcNode.hasAttr(attrName):
            pm.displayWarning('The attribute {} does not exist in {}.'.format(attrName, srcNode))
            return
        
        srcAttr     = srcNode.attr(attrName)
        attrData    = cls.getAttrDict(srcAttr)
        if not attrData:
            return None
        
        #get src state
        srcValue         = srcAttr.get()
        srcLockState     = srcAttr.isLocked()
        srcCompoundState = srcAttr.isCompound()
        srcConnections   = cls.getAttrConnection(srcAttr)

        #if attribute is compound, read the children attribute info.
        srcChildInfo        = OrderedDict()
        srcChildConnections = OrderedDict()
        if srcCompoundState:
            for child in srcAttr.getChildren():
                srcChildInfo[child.attrName()]        = cls.getAttrDict(child)
                srcChildConnections[child.attrName()] = cls.getAttrConnection()
        
        #lock check
        check = []
        check.extend(srcConnections['inputs'])
        check.extend(srcConnections['outputs'])
        if srcCompoundState:
            for child in srcAttr.getChildren():
                check.extend(srcChildConnections[child.attrName()]['inputs'])
                check.extend(srcChildConnections[child.attrName()]['outputs'])
        
        list_locked = [ [ attr, attr.isLocked() ] for attr in check ]

        #unlock
        for attr in check:
            attr.unlock()
        
        if move:
            if srcAttr.isLocked():
                srcAttr.unlock()
            pm.deleteAttr(srcAttr)
        
        #create attribute
        cls.createAttr(tarNode, attrData)

        #if attribute is compound , create that.
        if srcCompoundState:
            for childKey in sorted(srcChildInfo.keys()):
                cls.createAttr(tarNode, srcChildInfo[childKey])
        newAttr = tarNode.attr(attrName)

        #copy value
        newAttr.set(srcValue)

        #copy lock state
        if srcLockState:
            newAttr.lock()
        else:
            newAttr.unlock()
        
        #connectAttribute
        cls.connectAttr(newAttr, **srcConnections)
        #if compound, child connect
        if srcCompoundState:
            for attrChild, attrKey in zip(newAttr.getChildren(), sorted(srcChildConnections.keys() ) ):
                cls.connectAttr(attrChild, **srcChildConnections[childKey])
        
        #lock all attribute
        for attr , _isLocked in list_locked:
            if _isLocked:
                attr.lock()
        
        return newAttr

    
    @classmethod
    def getSelectedAttrs(cls):
        attrs = pm.channelBox('mainChannelBox', q=1, sma=1)
        if not attrs:
            return []
        return attrs
    
    @classmethod
    def getAllUserAttrs(cls, node):
        allUd = []
        for attr in pm.listAttr(node, ud=1):
            if not node.attr(attr).parent():
                allUd.append(attr)
        return allUd

    @classmethod
    def getAttrConnection(cls, srcAttr):
        return { 'inputs': srcAttr.inputs(p=True), 'outputs':srcAttr.outputs(p=True) }
    
    @classmethod
    def selectAttr(cls, attributes, nodes):
        toSel = [ '{}.{}'.format(n, a) for a in attributes for n in nodes ]
        pm.select(nodes, r=1)
        strCmd = "import pymel.core as pm\npm.channelBox('mainChannelBox', e=1, select={}, update=1)"
        pm.evalDeferred(strCmd.format(toSel))
    
    @classmethod
    def moveUpAttr(cls, *args):
        selAttrs = cls.getSelectedAttrs()
        if not len(pm.ls(sl=1)) or not selAttrs:
            print('please select object.')
            return

        selItems = pm.selected()
        lastParent = None

        for item in selItems:
            for attribute in selAttrs:
                if item.attr(attribute).parent():
                    attribute = item.attr(attribute).parent().attrName()
                    if attribute == lastParent:
                        continue
                    lastParent = attribute
                
                allAttrs = cls.getAllUserAttrs(item)

                if attribute not in allAttrs:
                    continue
                
                posAttr = allAttrs.index(attribute)
                if posAttr == 0:
                    continue
                belowAttr = allAttrs[posAttr - 1:]
                belowAttr.remove(attribute)

                res = cls.copyAttr(item, item, attribute, move=1)
                if not res:
                    return
                
                for attr in belowAttr:
                    res = cls.copyAttr(item, item, attr, move=1)
                    if not res:
                        return
        cls.selectAttr(selAttrs, selItems)

    @classmethod
    def moveDownAttr(cls, *args):
        selAttrs = cls.getSelectedAttrs()
        if not len(pm.ls(sl=1)) or not selAttrs:
            print('please select object.')
            return

        selItems = pm.selected()
        lastParent = None

        for item in selItems:
            for attribute in reversed(selAttrs):
                if item.attr(attribute).parent():
                    attribute = item.attr(attribute).parent().attrName()
                    if attribute == lastParent:
                        continue
                    lastParent = attribute
                
                allAttrs = cls.getAllUserAttrs(item)

                if attribute not in allAttrs:
                    continue
                
                posAttr = allAttrs.index(attribute)
                if posAttr == len(allAttrs) - 1:
                    continue
                belowAttr = allAttrs[posAttr + 2:]

                res = cls.copyAttr(item, item, attribute, move=1)
                if not res:
                    return
                
                for attr in belowAttr:
                    res = cls.copyAttr(item, item, attr, move=1)
                    if not res:
                        return
        cls.selectAttr(selAttrs, selItems)
    
    @classmethod
    def createAttr(cls, node, attrData):
        attrName = attrData['ln']
        if node.hasAttr(attrName):
            pm.displayWarning('attribute {} already exist in {}.'.format(attrName, node))
        else:
            attrData = convert_keys_to_string(attrData)
            pm.addAttr(node, **attrData)
    
    @classmethod
    def connectAttr(cls, attribute, inputs=None, outputs=None, **kwargs):
        if inputs:
            for attrInput in inputs:
                if attribute.inputs():
                    cls.sharedConnection(attrInput, attribute)
                else:
                    attrInput.connect(attribute)
        if outputs:
            if isNumericAttr(attribute.type()):
                for attrOutput in outputs:
                    if attrOutput.inputs(p=1):
                        cls.shared_connection(attribute, attrOutput)
                    else:
                        attribute.connect(attrOutput)

    @classmethod
    def sharedConnection(cls, srcAttr, tarAttr):
        preConnectAttr = get1st(tarAttr.inputs(p=1))

        pb = pm.createNode('pairBlend', ss=1)
        pb.w.set(0.5)
        dataPre = { True: pb.inTranslate1, False: pb.inTranslateX1 }
        dataSrc = { True: pb.inTranslate2, False: pb.inTranslateX2 }
        dataOut = { True: pb.outTranslate, False: pb.outTranslateX }

        #check isCompoumd attribute.
        _isCompound = preConnectAttr.isCompound()
        preConnectAttr.connect(dataPre[_isCompound])
        srcAttr.connect(dataSrc[_isCompound])
        dataOut[_isCompound].connect(tarAttr, force=1)
    
    
    @classmethod
    def addDivision(cls, *args):
        """add a divider attribute in channelBox.
            attribute type is enum.
            e.g.) --------
        """
        item = getLast(pm.selected())
        name = 'divider'
        cont = 0
        fullname = name + str(cont).zfill(2)

        while fullname in [ attr.attrName() for attr in item.listAttr(ud=1) ]:
            cont += 1
            fullname = name + str(cont).zfill(2)
        
        d_data               = OrderedDict()
        d_data['ln']         = str(fullname)
        d_data['type']       = 'enum'
        d_data['nn']         = str(' ')
        d_data['hidden']     = False
        d_data['keyable']    = True
        d_data['enumName']   = (str('-'* 15))
        cls.createAttr(item, d_data)
    
    def unlockAttrs(self, *args):
        for item in pm.selected():
            for attr in itertools.product(['t', 'r', 's'], ['x', 'y', 'z']):
                item.attr(''.join(attr)).unlock()