#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

"""每日数据统计

使用crontab定时任务，每天01:15统计前天数据，部分数据如：
兑换订单由于审核状态修改，需重复统计前3天以获得准确数据。
"""

import yaml
import torndb
from utils import YamlLoader

from datetime import date, timedelta


SETTINGS_FILE = "settings.yaml"

# MySQL数据库连接配置
try:
    config = yaml.load(file(SETTINGS_FILE, 'r'), YamlLoader)
except yaml.YAMLError as e:
    print "Error in configuration file: %s" % e

# 数据库连接实例
db = torndb.Connection(**config['mysql'])

def users_stat(day_str):
    """ 统计用户 """
    keys = ['users_total', 'users_ios', 'users_aos']
    result = {}.fromkeys(keys, 0)
    users_stat = db.query(
        "SELECT platform, count(`uid`) AS dcount FROM `users` "
        "WHERE date(`create_at`) = %s GROUP BY `platform`", day_str)
    for u in users_stat:
        result['users_total'] += u['dcount']
        if u['platform'] == 1:
            result['users_ios'] = u['dcount']
        if u['platform'] == 2:
            result['users_aos'] = u['dcount']

    return result

def earns_stat(day_str):
    """ 赚取统计 """
    keys = ['earns_c', 'earns_e', 'earns_d']
    result = {}.fromkeys(keys, 0)
    earns_stat = db.get(
        "SELECT SUM(`price`) AS dprice, SUM(`points`) AS dpoints, COUNT(`id`) AS dcount "
        "FROM `callback_orders` WHERE date(`time`) = %s", day_str)
    result = {}.fromkeys(earns_stat.keys(), 0)
    earns = [('dprice', 'earns_c'),
             ('dpoints', 'earns_e'),
             ('dcount', 'earns_d')]
    for e in earns:
        if earns_stat[e[0]]:
            result[e[1]] = earns_stat[e[0]]

    return result

def finance_stat(day_str):
    """ 财务统计 """
    keys = ['coupon', 'duiba_order', 'reject_order']
    result = {}.fromkeys(keys, 0)
    # 兑吧优惠劵
    coupons_stat = db.get(
        "SELECT sum(`price`) AS dsum FROM `exchange_orders` "
        "WHERE `type` = 'coupon' AND date(`create_time`) = %s",
        day_str
    )
    result['coupon'] = coupons_stat['dsum'] if coupons_stat['dsum'] else 0

    # 兑吧兑换
    duiba_stat = db.get(
        "SELECT sum(`total_price`) AS dsum FROM `exchange_orders` "
        "WHERE `status` in (10, 11, 12, 13, 14) AND date(`create_time`) = %s",
        day_str
    )
    result['duiba_order'] = duiba_stat['dsum'] if duiba_stat['dsum'] else 0

    # 延缓/忽略/拒绝
    reject_stat = db.get(
        "SELECT sum(`total_price`) AS dsum FROM `exchange_orders` "
        "WHERE `status` in (12, 14) AND date(`create_time`) = %s",
        day_str
    )
    result['reject_order'] = reject_stat['dsum'] if reject_stat['dsum'] else 0

    return result

def promote_stat(day_str):
    """ 推广统计 """
    promotes = db.query("SELECT * FROM `promote` WHERE `status` = 1")
    for pro in promotes:
        user_info = db.get("SELECT * FROM `users` WHERE `uid` = %s", pro['uid'])
        total_invites = user_info['invites']
        total_iv_points = user_info['iv_points']
        last = db.get(
            "SELECT * FROM `promote_static` WHERE `uid` = %s "
            "ORDER BY `id` DESC LIMIT 1", pro['uid'])
        if last:
            diff_invites = total_invites - last['total_invites']
            diff_iv_points = total_iv_points - last['total_iv_points']
        else:
            diff_invites = total_invites
            diff_iv_points = total_iv_points
        db.execute(
            "INSERT INTO `promote_static` (`uid`, `group`, `total_invites`, "
            "`total_iv_points`, `diff_invites`, `diff_iv_points`, `time`)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            pro['uid'], pro['group'], total_invites, total_iv_points,
            diff_invites, diff_iv_points, day_str)

def _check_exists(day_str):
    """ 判断数据库是否存在该天数据 """
    flag = db.get(
        "SELECT `id` FROM `summary` WHERE `time` = %s", day_str)
    exists = True if flag else False
    return exists

def store_users(day_str):
    """ 保存用户统计数据 """
    users = users_stat(day_str)
    exists = _check_exists(day_str)
    if not exists:
        db.execute(
            "INSERT INTO `summary`(`time`, `users_total`, `users_ios`, `users_aos`)"
            "VALUES(%s, %s, %s, %s)",
            day_str, users['users_total'], users['users_ios'], users['users_aos'])
    else:
        db.execute(
            "UPDATE `summary` SET `users_total` = %s, `users_ios` = %s, `users_aos` = %s "
            "WHERE `time` = %s",
            users['users_total'], users['users_ios'], users['users_aos'], day_str)

def store_earns(day_str):
    """ 保存赚取统计数据 """
    earns = earns_stat(day_str)
    exists = _check_exists(day_str)
    if not exists:
        db.execute(
            "INSERT INTO `summary`(`time`, `earns_d`, `earns_e`, `earns_c`)"
            "VALUES(%s, %s, %s, %s)",
            day_str, earns['earns_d'], earns['earns_e'], earns['earns_c'])
    else:
        db.execute(
            "UPDATE `summary` SET `earns_d` = %s, `earns_e` = %s, `earns_c` = %s "
            "WHERE `time` = %s",
            earns['earns_d'], earns['earns_e'], earns['earns_c'], day_str)

def store_finance(day_str):
    """ 保存数据至数据库中 """
    finance = finance_stat(day_str)
    exists = _check_exists(day_str)
    if not exists:
        db.execute(
            "INSERT INTO `summary`(`time`, `coupon`, `duiba_order`, `reject_order`)"
            "VALUES(%s, %s, %s, %s)",
            day_str, finance['coupon'], finance['duiba_order'], finance['reject_order'])
    else:
        db.execute(
            "UPDATE `summary` SET `coupon` = %s, `duiba_order` = %s, `reject_order` = %s "
            "WHERE `time` = %s",
            finance['coupon'], finance['duiba_order'], finance['reject_order'], day_str)


if __name__ == "__main__":
    today = date.today()
    yesterday = today - timedelta(days=1)
    yes_str = yesterday.strftime("%Y-%m-%d")
    # 推广数据统计
    promote_stat(yes_str)
    # 存储赚取统计， 一天前数据
    store_earns(yes_str)
    # 存储财务统计，一二三天前数据
    for n in range(3):
        day = yesterday - timedelta(days=n)
        day_str = day.strftime("%Y-%m-%d")
        store_users(day_str)
        store_finance(day_str)
