#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

import db

# 奖励类型
INVITE_REGISTER = 1
INVITE_PRORATA = 2

def new_invite(oid, uid, invite, typ, points):
    return db.mysql.execute(
        "INSERT INTO `invite_re` (`oid`, `uid`, `prize`, `typ`, `invite_uid`)"
        "VALUES (%s, %s, %s, %s, %s)", oid, uid, points, typ, invite)

def get_my_invites(uid):
    return db.mysql.query(
        "SELECT a.`time`, b.`name` FROM `invite_re` AS a "
        "LEFT JOIN `users` AS b ON a.`invite_uid` = b.`uid` "
        "WHERE a.`uid` = %s AND a.`typ` = 1 "
        "ORDER BY `id` DESC ", uid)
