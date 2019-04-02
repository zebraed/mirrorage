#! /usr/bin/env python
# -*- coding : utf-8 -*-
# vim:fenc=utf-8
# name : cmdModule.py
# Copyright (c) 2019 / author : R.O a.k.a last_scene
# since 2019 -
# Distributed under terms of the MIT license.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future_builtins import map
from future_builtins import filter

from abc import ABCMeta, abstractmethod


class CmdModule(ABCMeta):
    name = 'command module'

    @abstractmethod
    def execute(self, *args):
        print('This is command module.')