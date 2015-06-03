#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author chenjiehua@youmi.net
#
"""订单自动拒绝

根据用户的微信号性别为空判定其为非法用户，
筛选订单，7个小时候自动设置为非法订单
"""

import yaml
import torndb
import requests
import utils
import hashlib
import time
from utils import YamlLoader

try:
    import ujson as json
except ImportError:
    import json

SETTINGS_FILE = "settings.yaml"
SLEEP_TIME = 3600
db = None
config = None


def main():
    global db, config
    try:
        config = yaml.load(file(SETTINGS_FILE, 'r'), YamlLoader)
    except yaml.YAMLError as e:
        print "Error in configuration file: %s" % e
        return

    log_path = config['log']['autoban_log']
    db = torndb.Connection(**config['mysql'])

    while True:
        params, succ, msg = duiba()
        info = '%s %s' % (params['rejectOrderNums'], msg)
        utils.print_log('autoban', log_path, info)
        time.sleep(SLEEP_TIME)


def get_orders():
    """ 筛选订单 """
    orders = db.query(
        "SELECT a.* FROM `exchange_orders` AS a "
        "LEFT JOIN `users` AS b ON a.uid=b.uid "
        "WHERE b.sex = 0 AND a.status=10 ")

    order_str = ''
    for o in orders:
        datas = db.query("SELECT `id` FROM `exchange_orders` WHERE `address` = %s GROUP BY `uid`", o['address'])
        if len(datas)>1:
            db.execute("UPDATE `exchange_orders` SET `status` = 12 WHERE `id` = %s", o['id'])
            order_str += o['orderNum'] + ','

    return order_str

def sign(params={}):
    """ 生成签名参数 """
    def ksort(d):
        return [(k, d[k]) for k in sorted(d.keys())]

    params['appSecret'] = config['duiba']['appSecret']
    sorted_params = ksort(params)
    raw_str = ''
    for p in sorted_params:
        raw_str += str(p[1])
    sign = hashlib.new('md5', raw_str).hexdigest()
    return sign

def duiba():
    timestamp = int(time.time() * 1000)
    reject_order = get_orders()
    appKey = config['duiba']['appKey']
    params = {'passOrderNums': '', 'rejectOrderNums': reject_order,
              'timestamp': timestamp, 'appKey': appKey}
    params['sign'] = sign(params)
    url = 'http://www.duiba.com.cn/audit/apiAudit'
    r = requests.get(url, params=params)
    result = json.loads(r.text.replace('\'', '\"'))
    if result['success']:
        return params, True, ''
    else:
        return params, False, result['errorMessage']

if __name__ == "__main__":
    main()
