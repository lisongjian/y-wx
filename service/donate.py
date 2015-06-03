#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

""" 捐款活动相关 """

import constants
import IP

from models import users, orders
from protocols import WebBaseHandler

try:
    import ujson as json
except ImportError:
    import json

class DonateShareHandler(WebBaseHandler):
    """ 捐款倡议 """

    def get(self):
        pass


class DonatePageHandler(WebBaseHandler):
    """ 捐款页面 """

    def get(self):
        code = self.get_argument('code', None)
        if not code:
            redirect_uri = urlparse.urljoin(constants.SITE_BASEURL, 'v1/donate/page')
            url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=%s&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect' % (constants.WX_APPID, redirect_uri)
            self.redirect(url, False, 302)
            return

        # 通过code获取openid
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        params = {
            "appid": constants.WX_APPID,
            "secret": constants.WX_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        }
        r = requests.get(url, params=params)
        result = r.json()
        if result.get('errcode', None):
            url = urlparse.urljoin(constants.SITE_BASEURL, 'v1/donate/page')
            self.redirect(url)
            return

        # 判断用户是否已经关注
        user_info = users.get_info(result['openid'])
        if user_info and user_info.get('status') == 0:
            self.render('')

        else:
            self.render('')


class DonateActionHandler(WebBaseHandler):
    """ 捐款 """

    def post(self):
        openid = self.get_argument('openid', '')
        if not openid:
            self.return_result(constants.ERR_INVALID_PARAMS)
            return

        price = self.get_argument('price', 0)
        if price.isdigit() and int(price) <= 0:
            self.return_result(constants.ERR_PRICE_NULL)
            return

        user_info = users.get_info(arg['openid'])
        points = int(price) * 1000
        if user_info['points'] < points:
            self.return_result(constants.ERR_NOT_POINTS)
            return

        oid = orders.new_global_order(user_info['uid'], -points, user_info['points'],
                orders.ORDER_TYP_EXCHANGE, u'云南地震捐款 %s 元' % price)
        ip = self.requests.remote_ip
        ip_address = IP.find(ip)
        p = {
            'uid': user_info['uid'],
            'oid': oid,
            'ip': ip,
            'ip_address': ip_address,
            'points': points,
            'total_points': points,
            'price': price,
            'total_price': price,
            'goods_id': 1,
            'goods_title': u"捐款 %s 元" % price,
            'count': 1,
            'status': 13,
            'address_type': 0,
            'address': user_info['name'],
            'notes': u"%s 捐款 %s 元" % (user_info['name'], price),
            'orderNum': None,
            'type': None,
        }
        orders.new_exchange_order(p)
        users.sub_exchange_points(user_info, points)
        self.return_result((0, '捐款成功！'))

    def return_result(self, result):
        res = {"c": result[0], "d": result[1]}
        self.write_json(res)
        return
