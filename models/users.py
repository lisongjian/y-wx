#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author: chenjiehua@youmi.net
#
""" 用户信息相关操作 """

import db


def new_user(openid, name, sex, city, country, province, invite_by):
    return db.mysql.execute(
        "INSERT INTO `users` (`openid`, `name`, `sex`, `city`, \
        `province`, `country`, `invite_by`)"
        "VALUES(%s, %s, %s, %s, %s, %s, %s)",
        openid, name, sex, city, province, country, invite_by)

def get_info(openid):
    return db.mysql.get("SELECT * FROM `users` WHERE `openid` = %s", openid)

def get_info_by_uid(uid):
    return db.mysql.get("SELECT * FROM `users` WHERE `uid` = %s", uid)

def incr_invites(user_info):
    invites = user_info['invites'] + 1
    return db.mysql.execute(
        "UPDATE `users` SET `invites` = %s WHERE `uid` = %s",
        invites, user_info['uid'])

def set_headimg(uid, headimg):
    return db.mysql.execute(
        "UPDATE `users` SET `headimg` = %s WHERE `uid` = %s",
        headimg, uid)

def set_ip(openid, ip, ip_address, platform):
    return db.mysql.execute(
        "UPDATE `users` SET `ip` = %s, `ip_address` = %s, `platform` = %s "
        "WHERE `openid` = %s", ip, ip_address, platform, openid)

def set_status(openid, status):
    return db.mysql.execute(
        "UPDATE `users` SET `status` = %s WHERE `openid` = %s", status, openid)

def set_first_task(uid):
    return db.mysql.execute(
        "UPDATE `users` SET `first_task` = 0 WHERE `uid` = %s", uid)

def add_points(user_info, add_points):
    points = user_info['points'] + int(add_points)
    return db.mysql.execute(
        "UPDATE `users` SET `points` = %s WHERE `uid` = %s",
        points, user_info['uid'])

def add_total_points(user_info, add_points):
    points = user_info['points'] + int(add_points)
    total_points = user_info['total_points'] + int(add_points)
    return db.mysql.execute(
        "UPDATE `users` SET `points` = %s, `total_points` = %s "
        "WHERE `uid` = %s", points, total_points, user_info['uid'])

def add_invite_points(user_info, add_points):
    points = user_info['points'] + add_points
    iv_points = user_info['iv_points'] + add_points
    total_points = user_info['total_points'] + add_points
    return db.mysql.execute(
        "UPDATE `users` SET `points` = %s, `iv_points` = %s, "
        "`total_points` = %s WHERE `uid` = %s",
        points, iv_points, total_points, user_info['uid'])

def add_exchange_points(user_info, add_points):
    points = user_info['points'] + add_points
    ex_points = user_info['ex_points'] - add_points
    return db.mysql.execute(
        "UPDATE `users` SET `points` = %s, `ex_points` = %s "
        "WHERE `uid` = %s", points, ex_points, user_info['uid'])

def sub_exchange_points(user_info, sub_points):
    points = user_info['points'] - sub_points
    ex_points = user_info['ex_points'] + sub_points
    return db.mysql.execute(
        "UPDATE `users` SET `points` = %s, `ex_points` = %s "
        "WHERE `uid` = %s", points, ex_points, user_info['uid'])

def get_users_rank():
    return db.mysql.query(
        "SELECT `uid`, `name`, `total_points`, `headimg` "
        "FROM `users` ORDER BY `total_points` DESC LIMIT 15")

if __name__ == "__main__":
    print get_users_rank()
