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
import maya.OpenMayaUI as omUI

from mirrorage.qtpy.Qt import QtCore, QtGui, QtWidgets

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import os
import sys
import functools
import subprocess
import platform

from .. import utils as utils


maya_ver = int(cmds.about(v=1)[:4])
maya_api_ver = int(cmds.about(api=1))


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
    
    def setAnimationSize(self, **kwargs):
        #utils.getFlag(kwargs, [])
        self.anim = QtCore.QPropertyAnimation(self, 'geometry')
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuint)
        x = self.geometry().x()
        y = self.geometry().y()

        self.anim.setEndValue(QtCore.QRect(x, y, wid, hei))
        self.anim.start()
    
    #================#
    #virtual function#
    #=================
    def setLayout(self, mainWidget):
        pass


class SubWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        super(SubWidget, self).__init__(*args, **kwargs)
    

class RightClickButton(QtWidgets.QPushButton):
    rightClicked = QtCore.Signal()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super(self.__class__, self).mouseReleaseEvent(event)


def separator(bold=1, style='solid', color='#aaa'):
    lbl   = QtWidgets.QLabel()
    style = 'QLabel{border: ' + '{bold}px solid {color}; border-style: nonoe none {style} node; font-size:2px;'\
    .format(bold=bold, style=style, color=color) + '}'
    lbl.setStyleSheet(style)
    return lbl


def radioButtonGrp(nrb=2, l='sample :', sl=1, **kwargs):
    HL  = QtWidgets.QHBoxLayout()
    lbl = QtWidgets.QLabel(l, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    HL.addWidget(lbl)

    rb_list = []
    for i in range(nrb):
        bl = utils.getFlag(kwargs, ['bl{}'.format(i+1)], 'None')
        rb = QtWidgets.QRadioButton(bl)
        if i == sl - 1:
            rb.setChecked(1)
        HL.addWidget(rb)
        rb_list.append(rb)

    return [HL] + rb_list


def checkBoxGrp(ncb=3, l='sample :', sl=[], **kwargs):
    HL  = QtWidgets.QHBoxLayout()
    lbl = QtWidgets.QLabel(l, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    HL.addWidget(lbl)

    cb_list = []
    for i in range(ncb):
        bl = utils.getFlag(kwargs, ['bl{}'.format(i+1)], 'None')
        cb = QtWidgets.QCheckBox(bl)
        if sl[i]:
            cb.setChecked(1)
        HL.addWidget(cb)
        cb_list.append(cb)
    
    return [HL] + cb_list