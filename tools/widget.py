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
import time
from abc import ABCMeta, abstractmethod

from . import utils as utils


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

    __metaclass__ = ABCMeta

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
    
    @abstractmethod
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


class RightClickToolButton(QtWidgets.QToolButton):
    rightClicked = QtCore.Signal()
    def mouseReleaseEvent(self, e):
        if e.button() == Qt.RightButton:
            self.rightClicked.emit()
        else:
            super(self.__class__, self).mouseReleaseEvent(e)


class CustomDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, f=0):
        super(CustomDialog, self).__init__(parent, f)
    
    def setLayout():
        pass


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


def textFieldButtonGrp(l="label", tx="", bl="", bc="", **kwargs):
    cw1        = kwargs.setdefault('cw1', 100)
    optBTN1    = kwargs.setdefault('bl1', None)
    optBTNCmd1 = kwargs.setdefault('bc1', None)
    tbHL = QtWidgets.QHBoxLayout()

    tbLBL = QtWidgets.QLabel(l)
    tbLBL.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    tbLBL.setFixedWidth(cw1)
    tbHL.addWidget(tbLBL)

    tbLE = QtWidgets.QLineEdit(tx)
    tbHL.addWidget(tbLE)

    if bl != "":
        tbPB = QtWidgets.QPushButton(bl)
        if bc == "":
            bc = lambda *args:tbLE.setText(pm.cmds.ls(sl=1)[0] if len(pm.ls(sl=1)) > 0 else "")
        tbPB.clicked.connect(bc)
        tbHL.addWidget(tbPB)

    if optBTN1 is not None:
        optPB1 = QtWidgets.QPushButton(optBTN1)
        optPB1.clicked.connect(optBTNCmd1)
        tbHL.addWidget(optPB1)

    return tbHL, tbLE


def fileDialog(parent, mode, **kwargs):
    """mult file dialog util function.
    """
    dir_path      = utils.getFlag(kwargs, ['dir_path', 'dp'], os.path.expanduser('~'))
    title         = utils.getFlag(kwargs, ['title', 't'], '{} File'.format(mode.capitalize()))
    dir_only      = utils.getFlag(kwargs, ['dir_only', 'do'], False)
    filters       = utils.getFlag(kwargs, ['filters', 'fl'], 'Json Files (*.json)')
    select_filter = utils.getFlag(kwargs, ['select_filter', 'slf'], 'Json Files (*.json)')
    options       = utils.getFlag(kwargs, ['options', 'op'], QtWidgets.QFileDialog.DontUseNativeDialog)
    mult          = utils.getFlag(kwargs, ['mult', 'm'], False)

    dialog = QtWidgets.QFileDialog()
    if mode == 'open':
        if not dir_only:
            if not mult:
                fp = dialog.getOpenFileName(parent, title, dir_path, filters, select_filter, options)
            else:
                fp = dialog.getOpenFileNames(parent, title, dir_path, filters, select_filter, options)
        else:
            options += dialog.DirectoryOnly|dialog.ShowDirsOnly
            fp = dialog.getExistingDirectory(parent, title, dir_path, options)
            
    elif mode == 'save':
        fp = dialog.getSaveFileName(parent, title, dir_path, filters, select_filter, options)            
    
    if fp.isEmpty():
        return
    fp = fp.replace('/', os.sep)
    return fp


def progressDialog(event, message, parent, button='Cancel', **kwargs):
    _max = 100
    _min = 0
    pDialog = QtWidgets.QProggressDialog(message, button, _min, _max, parent)
    pDialog.setWindowTitle('Progress Dialog')

    #a = processing_object
    for count in range(_max + 1):
        event.processEventd(QtCore.QEventLoop.ExcludeUserInputEvents)
        if pDialog.wasCanceled():
            break
        pDialog.setValue(count)
        pDialog.setLabelText(message + '%d %%' % count)
        #time.sleep(0.1)