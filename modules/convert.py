#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : convert.py
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
import maya.api.OpenMaya as om


def getMeshFromSelection():
    meshSelectionList = om.MGlobal.getActiveSelectionList()
    meshDag = meshSelectionList.getDagPath(0)
    return om.MFnMesh(meshDag)

def convertWorldUV(witch=0, pickPoint=(om.MPoint(0, 0, 0)), pickUVPoint=(0.5, 0.5), face='', **kwargs):
    """

    Return

    witch 1  ret[0], [1] ...UV point.
             ret[2]      ...UV num.
    
    witch 0 ... ret      ...world point.
    """
    meshMFn = getMeshFromSelection()
    if witch: #to world
        return meshMFn.getUVAtPoint(pickPos.om.MSpace.kWorld)
    else:     #to UV
        itrPol = om.MItMeshPolygon(om.MString(face))
        if itrPol.hasUVs():
            if face == '':
                return
            return meshMFn.getPointAtUV(face.getNum, pickUVPoint[0], pickUVPoint[1], om.MSpace.kWorkd)
        else:
            return