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

import json

from mirrorage.qtpy.Qt import QtCore, QtGui, QtWidgets

from .. import utils as utils
from .. import node as nd
from .. import widget as widget


class AttributeSplatterGUI(widget.BaseWidget):
    title = "Attribute Splatter"
    windowName = 'attributeSplatterWidget'

    def setLayout(self, mainWidget):
        
        mainVL = QtWidgets.QVBoxLayout()
        mainWidget.setLayout(mainVL)

        #mainVL.addWidget(QtWidgets.QLabel)

        HV   = QtWidgets.QHBoxLayout()
        exPB = QtWidgets.QPushButton('Export')
        exPB.clicked.connect(self.saveJsonFile)
        imPB = QtWidgets.QPushButton('Import')
        imPB.clicked.connect(self.openJsonFile)

        HV.addWidget(exPB)
        HV.addWidget(imPB)

        self.psL, self.psLE = widget.textFieldButtonGrp(l='Set Node :', bl='set', cwl='90')

        self.userOnly = QtWidgets.QCheckBox('Only user defined attribute', checked=1)
        mainVL.addWidget(self.userOnly)
        mainVL.addLayout(self.psL)


        mainVL.addStretch()
    
    def getOpenPath(self, filterType=['json']):
        self.openPath = widget.fileDialog(self, mode='open')
    
    def getSavePath(self):
        self.savePath = widget.fileDialog(self, mode='save')
    
    def saveJsonFile():
        pass

    
    @widget.undo
    def cmd(self, *args ,**kwargs):
        pass