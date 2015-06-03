#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author cairuitao@gmail.com
#

import os.path


""" Tornado Server 定义 """
# 接收到关闭信号后多少秒后才真正重启
MAX_WAIT_SECONDS_BEFORE_SHUTDOWN = 1
# Listen IPV4 only
IPV4_ONLY = True


""" 全局配置常量 """

TOKEN = 'quanminzuanqian'
WX_APPID = 'wx9a7e5db5f0a1a766'
WX_SECRET = '1353ab7481d96fcfe83bd54c5b0cee7c'

IOS_APPID = '07a7b3c83b747cfa'
IOS_SECRET = 'c2d01f125a6f19e2'
IOS_SERVER_KEY = '724b00056c84d2fb'

AOS_APPID = 'bc9c17453e0e1172'
AOS_SECRET = 'e84716155fdf4660'
AOS_SERVER_KEY = 'efbef33666479982'

SITE_BASEURL = "http://wechat.quanminzq.com/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

""" 用户相关 """
ERR_INVALID_USER = (-1001, '非法用户')


""" 兑换相关错误信息 """
ERR_INVALID_GOODS_COUNT = (-4001, "兑换商品数量错误")
ERR_NOT_ENOUGH_POINTS = (-4002, "余额不足")
ERR_INVALID_GOODS_ID = (-4003, "错误的商品编号")
ERR_EXCHANGE_MUCH = (-4004, "该兑换地址已超出当天正常兑换次数")
ERR_INVALID_ADDRESS = (-4005, "兑换地址非法")


""" 兑吧接口 """
ERR_KEY_NOT_MATCH = (-6001, 'AppKey不匹配')
ERR_TIME_NOT_NULL = (-6002, '时间戳不能为空')
ERR_INVALID_TIME = (-6003, '时间戳无效')
ERR_INVALID_SIGN = (-6004, '签名验证失败')


""" 捐款相关 """
ERR_INVALID_PARAMS = (-7001, '参数错误')
ERR_NOT_POINTS = (-7002, '积分不足')
ERR_PRICE_NULL = (-7003, '捐款金额无效')
