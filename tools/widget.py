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
from maya import OpenMayaUI

from mirrorage.qtpy.Qt import QtCore, QtGui, QtWidgets
from mirrorage.tools import *

#from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

try:
    import shiboken
except:
    import shiboken2 as shiboken

ptr = OpenMayaUI.MQtUtil.mainWindow()
parent = shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)


import os
import sys
import functools
import subprocess
import platform
import time
from abc import ABCMeta, abstractmethod


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


class BaseWidget(QtWidgets.QMainWindow):
    """
    Bass pyside widgets class for general use.

    """
    title      = ''
    windowName = 'newGUI'
    qss_path   = '_default'

    def __init__(self, *args, **kwargs):
        super(BaseWidget, self).__init__(parent)

        if pm.window(self.windowName, q=1, ex=1):
            pm.deleteUI(self.windowName)
        self.setObjectName(self.windowName)

        #define main widget.
        self.mainWidget = QtWidgets.QWidget()
        self.setLayout(self.mainWidget)

        pos = QtGui.QCursor().pos()
        self.setGeometry(QtCore.QRect(pos.x(), pos.y(), 300, 170))
        self.setFixedSize(300, 170)

        self.initUiElements()

        if self.qss_path != '':
            qss_pathName = self.qss_path
            if self.qss_path == '_default':
                qss_pathName = 'style.qss'
            qss_file = QtCore.QFile(os.path.dirname(__file__) + '/' + qss_pathName)
            qss_file.open(QtCore.QFile.ReadOnly)
            self.setStyleSheet(str(qss_file.readAll().data()))    
        
        #self.setting_file = os.path.join(os.getenv('MAYA_APP_DIR'), 'mirrorage_windowPref.ini')
        #self.pyside_setting = QtCore.QSettings(self.setting_file, QtCore.QSettings.IniFormat)
        #self.pyside_setting.setIniCodec('utf-8')

        #self.restore()

    def initUiElements(self):
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)

        #self.setWindowOpacity(0.90)

        p = QtGui.QPainter()
        radius = 10
        widget_rect = self.rect()
        rounded_rect = QtGui.QPainterPath()
        rounded_rect.addRoundedRect(QtCore.QRectF(0, 0, self.width(), self.height()-20), radius, radius)
        mask = QtGui.QRegion(rounded_rect.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.setWindowTitle(self.title)
        self.setCentralWidget(self.mainWidget)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setAttribute(QtCore.Qt.WA_AlwaysShowToolTips)

    def show(self):
        super(BaseWidget, self).show()

    def closeEvent(self, event):
        #if not self.isStarted():
        #    self.animation.start()
        #    self.isStarted = True
        #    event.ignore()
        #else:
        #    super(BaseWidget, self).closeEvent(event)

        #if self.pyside_setting:
        #    self.pyside_setting.setValue('windowState', self.saveState())
        #    self.pyside_setting.setValue(self.windowName + '-geom', self.saveGeometry)
        pass
    
    def restore(self):
        #if self.pyside_setting:
        #    setting = QtCore.QSettings(self.setting_file, QtCore.QSettings.IniFormat)
        #    #self.restoreState(self.pyside_setting.value("windowState"))
        #    self.restoreGeometry(self.pyside_setting.value(self.windowName + "-geom"))
        pass
    
    def addHelpDoc(self, path):
        mb = self.menuBar()
        help_menu = mb.addMenu('&Help')
        help_menu.addAction(QtWidgets.QAction('document', self, triggered=pm.Callback(self.open_file, path)))

    def open_file(self, path, ext='.md'):
        file_path = path.replace('.py', ext)
        pl = platform.system()
        if pl == 'Windows':
            os.startfile(file_path)
        elif pl == 'Darwin':
            os.startfile(file_path)
        elif pl == 'Linux':
            subprocess.call(['gedit-open', file_path])

    @abstractmethod
    def setLayout(self, mainWidget):
        pass


class CustomMoveAnimationWidget(BaseWidget):
    def __init__(self, *args, **kwargs):
        #self.mainWidget = parent
        super(CustomMoveAnimationWidget, self).__init__(*args, **kwargs)

        self.setWindowFlags(QtCore.Qt.Window              | 
                            QtCore.Qt.Tool                |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.X11BypassWindowManagerHint)
        self.__isDrag = False
        self.__startPos = QtCore.QPoint(0, 0)

        pal = QtGui.QPalette()
        self.setPalette(pal)
        
        self.setWindowOpacity(0.90)
        self.closeTimer = QtCore.QTimer(self, timeout=self.stop)

        self.btn = SysButton(self)
        self.btn.setText('Close')
        self.btn.setGeometry(0, 0, 40, 20)
        self.btn.clicked.connect(self.stop)
        self.closeWinButtonLayout = QtWidgets.QVBoxLayout()
        self.closeWinButtonLayout.addWidget(self.btn,  alignment=QtCore.Qt.AlignRight)

        #self.sizeVL = QtWidgets.QVBoxLayout()
        #sizeGrip = QtWidgets.QSizeGrip(self)
        #self.sizeVL.addWidget(sizeGrip, False, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.mainWidget.setLayout(self.closeWinButtonLayout)
        #self.mainWidget.setLayout(self.sizeVL)


    def inAnimation(self, startPos, endPos, nextAction=lambda:None):
        opacityAnimation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        opacityAnimation.setStartValue(0.0)
        opacityAnimation.setEndValue(0.9)

        opacityAnimation.setEasingCurve(QtCore.QEasingCurve.InQuad)
        opacityAnimation.setDuration(300)

        sizeAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        sizeAnimation.setStartValue(QtCore.QRect(startPos, QtCore.QSize(self.width(), 0)))
        sizeAnimation.setEndValue(QtCore.QRect(endPos, QtCore.QSize(self.width(), self.height())))
        sizeAnimation.setEasingCurve(QtCore.QEasingCurve.InQuad)
        sizeAnimation.setDuration(300)

        self.animGroup = QtCore.QParallelAnimationGroup(self)
        self.animGroup.addAnimation(opacityAnimation)
        self.animGroup.addAnimation(sizeAnimation)
        self.animGroup.finished.connect(nextAction)
        self.animGroup.start()
    
    def outAnimation(self, nextAction=lambda:None):
        opacityAnimation = QtCore.QPropertyAnimation(self, b'windowOpacity')
        opacityAnimation.setStartValue(0.9)
        opacityAnimation.setEndValue(0.0)
        sizeAnimation = QtCore.QPropertyAnimation(self, b'geometry')
        sizeAnimation.setStartValue(QtCore.QRect(self.pos(), QtCore.QSize(self.width(), self.height())))
        sizeAnimation.setEndValue(QtCore.QRect(QtCore.QPoint(
                                                            self.pos().x(),
                                                            self.pos().y()-50 ),
                                                            QtCore.QSize(self.width(), 0)))
        sizeAnimation.setEasingCurve(QtCore.QEasingCurve.InQuad)
        sizeAnimation.setDuration(300)

        opacityAnimation.setEasingCurve(QtCore.QEasingCurve.OutQuad)
        opacityAnimation.setDuration(300)

        del self.animGroup
        self.animGroup = QtCore.QParallelAnimationGroup(self)
        self.animGroup.addAnimation(opacityAnimation)
        self.animGroup.addAnimation(sizeAnimation)
        self.animGroup.finished.connect(nextAction)
        self.animGroup.start()
    
    def paintEvent(self, event):
        super(CustomMoveAnimationWidget, self).paintEvent(event)
    
    def stop(self):
        self.outAnimation(self.close)
    
    def close(self):
        super(CustomMoveAnimationWidget, self).close()

        self.closeTimer.stop()
        self.closeTimer.deleteLater()
        self.hide()
        self.animGroup.stop()
        self.deleteLater()
    
    def show(self, nextAction=lambda:None, closeTime=1000*10):
        super(CustomMoveAnimationWidget, self).show()
        self.geometry = QtWidgets.QApplication.desktop().availableGeometry()
        center = QtWidgets.QApplication.desktop().availableGeometry().center()
        framesize = self.frameSize()
        startPos = QtCore.QPoint(
                                self.geometry.width() / 2 - framesize.width() / 2,
                                self.geometry.height() / 2 - framesize.height() / 2 + self.mainWidget.height())
        endPos   = QtCore.QPoint(
                                self.geometry.width() / 2 - framesize.width() / 2,
                                self.geometry.height() / 2 - framesize.height() / 2 + self.mainWidget.height() + 10)
        self.move(center)

        self.inAnimation(startPos, endPos, nextAction=nextAction)
    
    def mousePressEvent(self, event):
        self.__isDrag = True
        self.__startPos = event.pos()
        super(CustomMoveAnimationWidget, self).mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        self.__isDrag = False
        super(CustomMoveAnimationWidget, self).mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.__isDrag:
            self.move(self.mapToParent(event.pos() - self.__startPos))
        super(CustomMoveAnimationWidget, self).mouseMoveEvent(event)
    
    def resizeEvent(self, QResizeEvent):
        super(CustomMoveAnimationWidget, self).resizeEvent(QResizeEvent)
        self.setFixedWidth(self.width())


class SysButton(QtWidgets.QPushButton):
    closed = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(SysButton, self).__init__(*args, **kwargs)
        self.clicked.connect(self.__closed)
    
    def __closed(self):
        self.closed.emit()


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

class Image(QtWidgets.QLabel):
    def __init__(self, fileName=None, parent=None):
        super(Image, self).__init__(parent)
        self.setImage(fileName)
    
    def setImage(self, fileName):
        self.setPixmap(QtWidgets.QPixmap(fileName))


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
        bl = getFlag(kwargs, ['bl{}'.format(i+1)], 'None')
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
        bl = getFlag(kwargs, ['bl{}'.format(i+1)], 'None')
        cb = QtWidgets.QCheckBox(bl)
        if sl[i]:
            cb.setChecked(1)
        HL.addWidget(cb)
        cb_list.append(cb)
    
    return [HL] + cb_list


def textFieldButtonGrp(l="label", tx="", bl="", bc="", **kwargs):
    cw1        = getFlag(kwargs, ['centerWidth1', 'cw1'], 100)
    optBTN1    = getFlag(kwargs, ['buttonLabel1', 'bl1'], None)
    optBTNCmd1 = getFlag(kwargs, ['buttonCommand', 'bc1'], None)
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
    dir_path      = getFlag(kwargs, ['dir_path',       'dp'], os.path.expanduser('~'))
    title         = getFlag(kwargs, ['title',           't'], '{} File'.format(mode.capitalize()))
    dir_only      = getFlag(kwargs, ['dir_only',       'do'], False)
    filters       = getFlag(kwargs, ['filters',        'fl'], 'Json Files (*.json)')
    select_filter = getFlag(kwargs, ['select_filter', 'slf'], 'Json Files (*.json)')
    options       = getFlag(kwargs, ['options',        'op'], QtWidgets.QFileDialog.DontUseNativeDialog)
    mult          = getFlag(kwargs, ['mult',            'm'], False)

    dialog = QtWidgets.QFileDialog()
    if mode == 'open':
        if not dir_only:
            if not mult:
                fp = dialog.getOpenFileName(parent, title, dir_path, filters, select_filter, options)[0]
            else:
                fp = dialog.getOpenFileNames(parent, title, dir_path, filters, select_filter, options)[0]
        else:
            options += dialog.DirectoryOnly|dialog.ShowDirsOnly
            fp = dialog.getExistingDirectory(parent, title, dir_path, options)[0]
            
    elif mode == 'save':
        fp = dialog.getSaveFileName(parent, title, dir_path, filters, select_filter, options)[0]
    
    if not fp:
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