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
from .. import node as node
from .. import widget as widget


class AttributeSplatterGUI(widget.BaseWidget):
    title = "Attribute Splatter"
    windowName = 'attributeSplatterWidget'

    def setLayout(self, mainWidget):
        
        mainVL = QtWidgets.QVBoxLayout()
        mainWidget.setLayout(mainVL)

        mainVL.addStretch()
    
    @widget.undo
    def cmd(self, *args ,**kwargs):
        pass