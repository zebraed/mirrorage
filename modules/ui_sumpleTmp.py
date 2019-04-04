import os
import cPickle as cPickle
from functools import partial

import imp
try:
    imp.find_module('PySide2')
    import PySide2.QtWidgets as QtWidgets
    import PySide2.QtGui as QtGui
    import PySide2.QtCore as QtCore
except ImportError:
    import PySide.QtGui as QtGui
    import PySide.QtCore as QtCore
try:
    imp.find_module("shiboken2")
    import shiboken2 as shiboken
except ImportError:
    import shiboken
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
import maya.OpenMayaAnim as OpenMayaAnim
import logging
logging.basicConfig(format='%(levelname)s: %(message)s')


class SkinIODialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SkinIODialog, self).__init__(parent)
        self.setWindowTitle()

class View(object):
    def __init__(self, model):
        self.model = model
    
    def register(self, controller):
        self.controller = controller

class Model(object):
    def __init__(self, view, model):
        pass

class Controller(object):
    def __init__(self, view, model):
        self.view = view
        self.model = model

        self.view.register(self)

if __name__ == '__main__':
    model = Model()
    view = View(model)
    controller = Controller(view, model)
