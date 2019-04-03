#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : markingMenu.py
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

from . import menuItems
from psychoid.modules import *

MENU_NAME = "markingMenu"

class MarkingMenu(menuItems.MenuItems):

    def __init__(self, *args, **kwargs):
        pass
    

    def _build(self):
        """Creates the marking menu context and call.
        """
        menu = pm.popupMenu(MENU_NAME,
                                     mm  = 1,
                                     b   = 2,
                                     aob = 1,
                                     ctl = 1,
                                     alt = 1,
                                     sh  = 0,
                                     p   = 'viewPanes',
                                     pmo = 1,
                                     pmc = self._buildMarkingMenu,
                                     )
    
    
    def _buildMarkingMenu(self, commands, menu, parent, **kwargs):
        """this is where all the elements of the marking menu our built.
           use to overwrite.
        """
        # Radial positioned
        pm.menuItem(p=menu, l="South West Button", rp="SW", c="print 'SouthWest'")
        pm.menuItem(p=menu, l="South East Button", rp="SE", c="print 'SouthEast'")
        pm.menuItem(p=menu, l="North East Button", rp="NE", c="pm.circle()")

        subMenu = pm.menuItem(p=menu, l="North Sub Menu", rp="N", subMenu=1)
        pm.menuItem(p=subMenu, l="North Sub Menu Item 1")
        pm.menuItem(p=subMenu, l="North Sub Menu Item 2")

        pm.menuItem(p=menu, l="South", rp="S", c="print 'South'")
        pm.menuItem(p=menu, ob=1, c="print 'South with Options'")

        # List
        pm.menuItem(p=menu, l="First menu item")
        pm.menuItem(p=menu, l="Second menu item")
        pm.menuItem(p=menu, l="Third menu item")
        pm.menuItem(p=menu, l="Create poly cube", c="pm.polyCube()")

        # Rebuild
        pm.menuItem(p=menu, l="Rebuild Marking Menu", c=rebuildMarkingMenu)