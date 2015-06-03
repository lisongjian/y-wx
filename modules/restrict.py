#!/usb/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author chenjiehua@youmi.net
#

import db
from models import options
from datetime import date


def valid_address_uid(address, uid):
    """ 单个address对应uid限制 """
    hashkey = "address_uid_%s" % str(address)
    valid = True
    r = db.redis
    if not r.sismember(hashkey, uid):
        r.sadd(hashkey, uid)

    max_repeat_uid = options.get('max_repeat_uid')
    if r.scard(hashkey) >= max_repeat_uid:
        valid = False
    return valid

def valid_address_day(address):
    """ 单个address一天兑换次数限制 """
    hashkey = "address_limit_%s" % str(address)
    valid = True
    r = db.redis
    today = date.today().strftime("%Y-%m-%d")
    if not r.hexists(hashkey, today):
        r.hset(hashkey, today, 1)
    else:
        exchange_times_d = options.get('exchange_times_d')
        if int(r.hget(hashkey, today)) < exchange_times_d:
            r.hincrby(hashkey, today)
        else:
            valid = False
    return valid
