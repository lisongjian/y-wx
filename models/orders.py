#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author cairuitao@gmail.com
#

import db


# 订单类型(1:任务,2:兑换)
ORDER_TYP_TASK = 1
ORDER_TYP_EXCHANGE = 2
ORDER_TYP_REGISTER = 3
ORDER_TYP_PRORATA = 4
ORDER_TYP_PRORATA_WEEK= 5

# 订单状态(10:审核, 11:通过, 12:拒绝, 13:成功, 14:失败)
ORDER_STS_DUI_AUDIT = 10
ORDER_STS_DUI_PASS = 11
ORDER_STS_DUI_REJECT = 12
ORDER_STS_DUI_SUCC = 13
ORDER_STS_DUI_FAIL = 14


def new_global_order(uid, points, last, typ, note):
    """新建全局订单"""
    return db.mysql.execute(
        "INSERT INTO `global_orders` (`uid`, `points`, `last`, `typ`, `note`)"
        "VALUES (%s, %s, %s, %s, %s)", uid, points, last, typ, note)

def get_global_orders(uid):
    return db.mysql.query(
        #"SELECT * FROM `global_orders` WHERE `uid` = %s AND `typ` in (1, 3, 4)"
        "SELECT * FROM `global_orders` WHERE `uid` = %s AND `typ` in (1, 3, 4,5)"
        "ORDER BY `id` DESC", uid)

def new_exchange_order(p):
    return db.mysql.execute(
        "INSERT INTO `exchange_orders` (`uid`, `oid`, `ip`, `ip_address`, `points`, "
        "`total_points`, `price`, `total_price`, `goods_id`, `goods_title`, `count`, "
        "`status`, `address_type`, `address`, `notes`, `orderNum`, `type`) "
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        p['uid'], p['oid'], p['ip'], p['ip_address'], p['points'], p['total_points'],
        p['price'], p['total_price'], p['goods_id'], p['goods_title'], p['count'],
        p['status'], p['address_type'], p['address'], p['notes'], p['orderNum'], p['type'])

def set_order_status(oid, status, notes):
    return db.mysql.execute(
        "UPDATE `exchange_orders` SET `status` = %s, `notes` = %s "
        "WHERE `oid` = %s", status, notes, oid)

def get_exchange_order(oid):
    return db.mysql.get(
        "SELECT * FROM `exchange_orders` WHERE `oid` = %s", oid)

def get_exchange_orders(uid):
    return db.mysql.query(
        "SELECT * FROM `exchange_orders` WHERE `uid` = %s "
        "ORDER BY `id` DESC", uid)

def new_callback_order(p):
    return db.mysql.execute(
        "INSERT INTO `callback_orders` (`order`, `oid`, `ad`, "
        "`adid`, `user`, `points`, `price`, `device`, `sig`, `platform`)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        p['order'], p['oid'], p['ad'], p['adid'], p['user'],
        p['points'], p['price'], p['device'], p['sig'], p['platform'])

def get_callback_orders(uid):
    return db.mysql.query(
        "SELECT * FROM `callback_orders` WHERE `user` = %s "
        "ORDER BY `id` DESC", uid)

def callback_order_exists(order):
    flag = db.mysql.get(
        "SELECT `id` FROM `callback_orders` WHERE `order` = %s", order)
    exist = True if flag else False
    return exist
