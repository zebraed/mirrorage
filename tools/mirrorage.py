#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : mirrorage.py
# Copyright (c) 2019/ author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.OpenMaya as om

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

import functools
import sys
import re

from collections import OrderedDict

__mod__ = ()
( reload(_m) for _m in __mod__ )

#mirror table
RE_LEFT_SIDE  = 'Lf|lf_|_lf|_l_|_L|L_|left|Left'
RE_RIGHT_SIDE = 'Rt|rt_|_rt|_r_|_R|R_|right|Right'

#daynamically define 
spL = RE_LEFT_SIDE.split('|')
left_side_dict  = { i:'{}'.format(spL[i]) for i in range(len(spL)) }

spR = RE_RIGHT_SIDE.split('|')
right_side_dict = { i:'{}'.format(spR[i]) for i in range(len(spR)) }

ANIMS = ('animCurveTL', 'animCurveTA', 'animCurveTU')


class MirrorAnimationCmd(object):
    pass

class MirrorAnimationGUI(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    title   = 'Mirrorage'
    winName = 'MirrorageWidget'
    
    def __init__(self, parent=None):
        super(MirrorAnimationGUI, self).__init__()

        if pm.window(self.winName, q=1, ex=1):
            pm.deleteUI(self.winName)
        self.setObjectName(self.winName)
        #TODO


def leftSide(node):
    global RE_LEFT_SIDE
    return findSide([node], RE_LEFT_SIDE)


def rightSide(node):
    global RE_RIGHT_SIDE
    return findSide([node], RE_RIGHT_SIDE)


def isLeftSide(name):
    side = leftSide(name)
    return matchSide(name, side)
    

def isRightSide(name):
    side = RightSide(name)
    return matchSide(name, side)


def sideToside(side, idx):
    global left_side_dict
    global right_side_dict
    if side == left_side_dict[idx]:
        return right_side_dict[idx]
    elif side == right_side_dict[idx]:
        return left_side_dict[idx]
    else:
        return False
    

def matchSide(name, side):

    if side:
        return side in name
    return False


def findSide(nodes, reSides, **kwargs):
    reSide = re.compile(reSides)
    for node in nodes:
        m = reSide.search(node)
        if m:
            return m.group(), True
        else:
            return '', False


def findSideDict(side, switch):
    global spL
    global spR
    if switch == 1:
        res = [ sideToside(side, i) for i in range(len(spL)) if spL[i] == side ]
        return res[0]
    elif switch == 2:
        res = [ sideToside(side, i) for i in range(len(spR)) if spR[i] == side ]
        return res[0]
    

def mirrorPlanes(mp='YZ', upAxis='Y'):
    """
    """
    if upAxis == 'Y':
        YZ = [ -1,  1,  1 ]
        XZ = [  1, -1,  1 ]
        XY = [  1,  1, -1 ]    
    elif upAxis == 'Z':
        YZ = [ -1, -1, -1 ]
        XZ = [  1, -1,  1 ]
        XY = [  1,  1, -1 ]
    
    mirror = eval(mp)    
    return mirror
    
    
def isAttrMirrored(attr, mirrorAxis):
    """
    """
    if mirrorAxis == [-1, 1, 1]:
        if attr == 'translateX' or attr == 'rotateY' or attr == 'rotateZ':
            return True
    
    elif mirrorAxis == [1, -1, 1]:
        if attr == 'translateY' or attr == 'rotateX' or attr == 'rotateZ':
            return True
    
    elif mirrorAxis == [1, 1, -1]:
        if attr == 'translateZ' or attr == 'rotateX' or attr == 'rotateY':
            return True
    
    elif mirrorAxis == [-1, -1, -1]:
        if attr == 'translateX' or attr == 'translateY' or attr == 'translateZ':
            return True
    
    return False
    
    
def mirrorObject(src, **kwargs):
    """this is Return the other/opposite side for the given name.
    """
    left,  id1  = leftSide(src)
    right, id2  = rightSide(src)
    
    if not id1:
        reside = findSideDict(right, 2)
        dst = src.replace(right, reside)
    elif not id2:
        reside = findSideDict(left, 1)
        dst = src.replace(left, reside)
    else:
        return
    return dst


def namespacesFromSelection():
    """this is get namespace string from current selectionList.
    """
    
    namespaces = ['']
    try:
        namespaces = a
    except NameError as error:
        pm.warning('occured nameError. skip get namespace.')
        namespaces = ['']
        
    return namespaces

        
def formatValue(value, **kwargs):
    return value*-1


def _maxIndex(num):
    m = 0
    result = 0
    for i in num:
        v = abs(float(i))
        if v > m:
            m = v
            result = num.index(i)
    return result


def getPy(arg):
    """this is conver to pymel object from string or unicode argument.
    """
    if isinstance(arg, basestring):
        return pm.PyNode(arg)
    else:
        return arg


def getAnimCurve(node, at, **kwargs):
    """this is get animCurve node from node name + attr name.

    Parameters
    ----------
    node : str or object
        get animCurve node has keyframe object.
    
    at   : str or object
        attribute.

    Returns
    -------
    object
        animCurve node.
    
    """
    global ANIMS
    
    node     = getPy(node)
    fullname = node.attr(at)
    con = pm.listConnections(fullname, d=0, s=1)
    if len(con) > 0 :
        if [ pm.nodeType(con[0]) == x for x in ANIMS ] :
            return con[0]
    else:
        pm.displayWarning('# animCurve node does not exist. skip.')
        return None


def getKeyTimeValue(animCurve, **kwargs):
    """this is get time and value dictionary from animCurve node attribute.

    Parameters
    ----------
    animCurve : str or object
        animCurve.

    Returns
    -------
    dict
        got keyframe has time and value dictonary.
    
    """
    animCurve = getPy(animCurve)
    indices   = animCurve.attr('ktv').get(mi=True)

    return OrderedDict( animCurve.attr('ktv[{}]'.format(i) ).get() for i in indices )


def extractKeyIndexTimeValue(dic={0 : 0}, frameRange=(0, 30), **kwargs):
    """this is extract animCurve's time and value in any frame range.

    Parameters
    ----------
    dic        : dict(in int or float)
        key = time, value = value.
    frameRange : tupple(in int or float)
        input spicifid range of frameRange.

    Returns
    -------
    dict
        ectracted keyframe has index, time and value dictonary.
    
    """
    
    range_idtv = OrderedDict()
    st, end    = frameRange
    
    idx = 0
    for t, v in dic.items():
        if st <= t and t <= end :
            range_idtv[idx] = { t : v }
        idx += 1
 
    return range_idtv


def scaleKey(node='', at='', value=True, frameRange=(0, 30), **kwargs):
    """this is wrap function. wrap based scaleKey command.

    Parameters
    ----------
    node : dict(in int or float)
            key = time, value = value.
            
    at   : tupple(in int or float)
            input spicifid range of frameRange.

    Returns
    -------
    dict
        extracted keyframe has time and value dictonary.
    
    """
    node     = getPy(node)
    
    fullname = node.attr(at)
    st, end  = frameRange
    
    curve    = getAnimCurve( node, at )
    
    if curve:
        if value:
            all_tv    = getKeyTimeValue(curve)
            toggle_tv = extractKeyIndexTimeValue(all_tv, frameRange=(st, end))
            for idx ,tv in toggle_tv.items():
                for v in tv.values():
                    pm.keyframe(fullname, e=1 ,index=idx, absolute=True ,valueChange=formatValue(v))
        else:
            pm.selectKey(curve)
            pm.scaleKey(iub=False, t=(st, end), ts=-1, tp=end / 2, fs=1, vs=1, vp=0, animation='keys')
            

def getNextKeyframe(node, at, **kwargs):
    """this Generators have a ``Yields`` section instead of a ``Returns`` section.

    Parameters
    ----------
    node : str or object
        The upper limit of the range to generate, from 0 to `n` - 1.

    at : str
        The upper limit of the range to generate, from 0 to `n` - 1.

    Yields
    ------
    start
        The next keyframe time in the range of k to n.

    Examples
    --------
    Examples should be written in doctest format, and should illustrate how
    to use the function.

    >>> print([i for i in getNextKeyframe()])
    [0, 2, 15, 24]

    """
    
    start = pm.findKeyframe(node, attribute=at, w='first')
    end   = pm.findKeyframe(node, attribute=at, w='last')
    yield start
    while True:
        next = pm.findKeyframe(node, attribute=at, time=(start, start), w='next')
        yield next
        if end == next:
            break;
        start = next


def getTimeRangeFromNode(node='', t=True, r=True, s=False, frameRange=(None,None), **kwargs):
    """this is get time range from node.
    
    Parameters
    ----------
    node        : str or object
                
    t           : bool
                translate on.
                
    r           : list[ str ]
                rotate on.
                
    mirrorAxis : list[ int ]
                mirroring axis list.

    Returns
    -------
     -
    
    """
    node = getPy(node)
    anim_curves = []
    if t:
        anim_curves += pm.listConnections(node, t='animCurveTL', et=1) 
    if r:
        anim_curves += pm.listConnections(node, t='animCurveTA', et=1)
    if s:
        anim_curves += pm.listConnections(node, t='animCurveTU', et=1)
        
    minTime, maxTime = frameRange
    
    for anim_curve in anim_curves:
        indices = anim_curve.attr('ktv').get(mi=True)
        for i in indices:
            k , _ = anim_curve.attr('ktv[{}]'.format(i)).get()
            if not minTime or k <= minTime:
                minTime = k
            elif not maxTime or maxTime <= k:
                maxTime = k
    
    return minTime, maxTime


def setAttr(name, attr, value, mirrorAxis=None):
    """wrap function. wrap based setAttr command.

    Parameters
    ----------
    name        : str or object
                
    attr        : str or object
                
    value       : list[ str ]
                    mirror target attribute.
                
    mirrorAxis  : list[ int ]
                    mirroring axis list.

    Returns
    -------
     -
    
    """
    if mirrorAxis is not None:
        value = formatValue(attr, value, mirrorAxis)
    
    try:
        cmds.setAttr(name + '.' + attr, value)
    except RuntimeError:
        return
        

def transferAnimation(src, dst, attrs=None, mirrorAxis=[], time=(None, None), **kwargs):
    """this is transfer animation keyframe to opposite side.

    Parameters
    ----------
    src        : str or object
                
    dst        : str or object
                translate on.
                
    attrs      : list[ str ]
                mirror target attribute.
                
    mirrorAxis : list[ int ]
                mirroring axis list.
                
    value      : tuple( int, int )
                toggle time range for based scale animation.

    Returns
    -------
     -
    
    """
    def _transferAnimation(src, dst, attrs=None, mirrorAxis=[], time=(None, None)):
        """inner method.
        """

        pm.cutKey(dst, time=time)
        if pm.copyKey(src, time=time or ()):
            if not time:
                pm.pasteKey(dst, option='replaceCompletely')
            else:
                pm.pasteKey(dst, option='replace')
        
        if attrs is None or attrs == [] :
            attrs = pm.listAttr(src, keyable=1) or []
            
        for at in attrs:
            if pm.objExists(dst):
                if dst.attr(at).isConnected():
                    if isAttrMirrored(at, mirrorAxis):
                        pm.scaleKey(dst.attr(at).name(), valueScale=-1, attribute=at)
                else:
                    value = src.attr(at).get()
                    setAttr(dst, at, value, mirrorAxis)

    src = getPy(src)
    dst = getPy(dst)

    try:
        _transferAnimation(src, dst, attrs, mirrorAxis, time=time)
    except:
        pm.displayWarning('error.')
        
                
def checkDouble3(t=True, r=True, s=False, **kwargs):
    """this is Return double3 standard keyable transform attributes.
    
    Parameters
    ----------
    t : bool
        add translate to list.
                
    r : bool
        add rotate to list.
                
    s : bool
        scale on.

    Returns
    -------
     list[ string ]
    
    """
    attrs = []
    if t:
        attrs += ('translateX', 'translateY', 'translateZ')
    if r:
        attrs += ('rotateX', 'rotateY', 'rotateZ')
    if s:
        attrs += ('scaleX', 'scaleY', 'scaleZ')
    return attrs


def mirrorAnimation(node='', t=True, r=True, s=False, value=True, frameRange=(None, None), **kwargs):
    """this is mirror value for animation object.
       Choose either value base scale mode or time base scale mode. 

    Parameters
    ----------
    node        : str or object
                
    t           : bool
                    translate on.
                
    r           : bool
                    rotate on.
                
    s           : bool
                    scale on.
                
    value       : bool
                    if True, value based scale. elif of, time based scale.

    frameRange  : tupple(int , int)
                    effective time range.
    
    mirrorAxis  : list[int, int, int]
                    mirror directions.
    
    mirrorPlane : string
                    mirror plane.

    Returns
    -------
     -
    
    """
    mirrorAxis  = kwargs.setdefault('mirrorAxis', [])
    mirrorPlane = kwargs.setdefault('mirrorPlane', 'XY')
    
    if node == '':
        node = pm.selected()[0]
    node        = getPy(node)
    
    dstSide     = mirrorObject(node.name())
    if dstSide == '':
        raise
    dstSide     = getPy(dstSide)
    
    st, end     = frameRange
    allrange    = False
    
    if not frameRange[0] or not frameRange[1]:
        allrange = True
    
    #mirror      = mirrorPlanes(mirrorPlane, upAxis)
    attrs       = checkDouble3(t, r, s)
    keyTimes    = getNextKeyframe(node, attrs)
    minTime     = st
    maxTime     = end
    if not allrange:
        for kt in keyTimes:
            if frameRange[0] <= kt:
                st = kt
                continue
            if kt <= frameRange[1]:
                end = kt
                continue
        if not st:
            st = 0
        if not end:
            end = pm.playbackOptions(q=1, max=1)
        rng = (st, end)
        minTime, maxTime = getTimeRangeFromNode( node, t=t, r=r, s=s, frameRange=rng )

    if value:
        if not t and not r and not s:
            pm.displayWarning('# Error no -t -r -s flags. Skip evaluate.')
            return
        else:
            transferAnimation(node, dstSide, attrs, mirrorAxis=mirrorAxis, time=(minTime, maxTime))
    else:
        for i in range(len(attrs)):
            if mirrorAxis[i] == -1:
                scaleKey(node, attrs[i], value, frameRange=(minTime, maxTime))