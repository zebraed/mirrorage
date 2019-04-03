#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : rigging.py
# Copyright (c) 2019 / author : R.O a.k.a last_scene
# Thanks to vshotarv.
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

from psychoid.modules import markingMenu
from psychoid.modules import *

MENU_NAME = "riggingMarkingMenu"

class RiggingMarkingMenu(markingMenu.MarkingMenu):

    def __init__(self, *args, **kwargs):
        super(RiggingMarkingMenu, self).__init__(*args, **kwargs)
        self._remove()
        self._build()
        print('Done!')
    
    def _buildMarkingMenu(self, commands, menu, parent, **kwargs):
        """this is where all the elements of the marking menu our built.
           use to overwrite.
        """
        # Radial positioned
        pm.menuItem(p=menu, l="Smooth Skin", rp="N", c="mel.elav('SmoothBindSkin;')")
        pm.menuItem(p=menu, ob=1, c="mel.eval('SmoothBindSkinOptions;')")

        constMenu = pm.menuItem(p=menu, l="Constraint", rp="E", subMenu=1)
        pm.menuItem(p=constMenu, l="Parent Constraint", rp="N", c="pm.parentConstraint(pm.selected()[:-1], pm.selected()[-1], mo=1)")
        pm.menuItem(p=constMenu, ob=1, c="mel.eval('ParentConstraintOptions;')")

        pm.menuItem(p=menu, l="North East Button", rp="NE", c="pm.circle()")

        #subMenu = pm.menuItem(p=menu, l="North Sub Menu", rp="N", subMenu=1)
        #pm.menuItem(p=subMenu, l="North Sub Menu Item 1")
        #pm.menuItem(p=subMenu, l="North Sub Menu Item 2")

        # List
        pm.menuItem(p=menu, l="First menu item")
        pm.menuItem(p=menu, l="Second menu item")
        pm.menuItem(p=menu, l="Third menu item")
        pm.menuItem(p=menu, l="Create poly cube", c="pm.polyCube()")

        # Rebuild
        pm.menuItem(p=menu, l="Rebuild Marking Menu", c=rebuildMarkingMenu)