#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

import db


def get(key):
    data = db.mysql.get("SELECT `values` FROM `options` WHERE `key` = %s", key)
    value = data['values'] if data else 0
    return value

def get_des(key):
    data = db.mysql.get("SELECT `description` FROM `options` WHERE `key` = %s", key)
    description = data['description'] if data else 0
    return description
