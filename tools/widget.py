#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : widget.py
# Copyright (c) 2019 / author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from future_builtins import map
from future_builtins import filter

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as om

from mirrorage.qtpy.Qt import QtCore, QtGui, QtWidgets

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import os
import sys
import functools
import subprocess
import platform


def undo(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            pm.undoInfo(ock=True)
            return func(*args, **kwargs)
        finally:
            pm.undoInfo(cck=True)
    
    return wrapper


class BaseWidget(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    """
    Bass pyside widgets class for general use.

    """
    title = ''
    windowName = 'newGUI'

    def __init__(self, parent=None, **kwargs):
        super(BaseWidget, self).__init__()

        if pm.window(self.windowName, q=1, ex=1):
            pm.deleteUI(self.windowName)
        self.setObjectName(self.windowName)

        self.mainWidget = QtWidgets.QWidget()

        self.setLayout(self.mainWidget)

        self.setWindowTitle(self.title)
        self.setCentralWidget(self.mainWidget)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips)

        setting_file = os.path.join(os.getenv('MAYA_APP_DIR'), 'mirrorage_windowPref.ini')
        self.pyside_setting = QtCore.QSettings(setting_file, QtCore.QSettings.IniFormat)
        self.pyside_setting.setIniCodec('utf-8')

    def restore(self):
        if self.pyside_setting:
            self.restoreGeometry(self.pyside_setting.value(self.windowName + '-geom'))
    
    def show(self):
        self.restore()
        super(BaseWidget, self).show()
    
    def closeEvent(self, event):
        if self.pyside_setting:
            self.pyside_setting.setValue(self.windowName + '-geom', self.saveGeometry)
    
    def addHelpDoc(self, path):
        mb = self.menuBar()
        help_menu = mb.addMenu('&Help')
        help_menu.addAction(QtWidgets.QAction('document', self, trriggered=pm.Callback(self.open_file, path)))

    def open_file(self, path, ext='.md'):
        file_path = path.replace('.py', ext)
        pl = platform.system()
        if pl == 'Windows':
            os.startfile(file_path)
        elif pl == 'Darwin':
            os.startfile(file_path)
        elif pl == 'Linux':
            subprocess.call(['gedit-open', file_path])
    
    #================#
    #virtual function#
    #=================
    def setLayout(self, mainWidget):
        pass