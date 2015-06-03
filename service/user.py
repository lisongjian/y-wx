#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

import urlparse
import utils
import constants

from protocols import WebBaseHandler
from models import users, orders, invites

class MyInfoHandler(WebBaseHandler):
    """ 我的信息 """

    def get(self):
        r = self.get_argument('r', '')
        if not r:
            self.write('参数错误')
            return
        openid = utils.decrypt(r)
        self.user_info = users.get_info(openid)
        if self.user_info['headimg']:
            uid_hash = utils.md5(self.user_info['uid'])
            headimg = urlparse.urljoin(constants.SITE_BASEURL, 'static/headimg/%s/%s/%s.png' \
                                % (uid_hash[0:2], uid_hash[2:4], self.user_info['headimg']))
        else:
	        headimg = urlparse.urljoin(constants.SITE_BASEURL, 'static/img/headimg.jpg')
        exchange_re = self.__get_exchange()
        earns_re = orders.get_global_orders(self.user_info['uid'])
        invite_re = invites.get_my_invites(self.user_info['uid'])
        self.render('info.html',
            user_info = self.user_info,
            exchange = exchange_re,
            earns = earns_re,
            invite = invite_re,
            headimg = headimg,
        )

    def __get_exchange(self):
        """ 兑换记录 """
        exchange_orders = orders.get_exchange_orders(self.user_info['uid'])
        datas = []
        status = [(10, '等待审核'),
                  (11, '正在兑换'),
                  (12, '拒绝兑换'),
                  (13, '兑换成功'),
                  (14, '兑换失败')]
        s = '等待审核' # 订单默认状态
        for o in exchange_orders:
            for sta in status:
                if o['status'] == sta[0]:
                    s = sta[1]
                    break
            tmp = {
                'title': o['goods_title'],
                'status': s,
                'time': o['create_time'],
            }
            datas.append(tmp)
        return datas


class MyRecordHandler(WebBaseHandler):
    """ 赚取记录 """

    def get(self):
        r = self.get_argument('r', '')
        if not r:
            self.write('参数错误')
            return
        openid = utils.decrypt(r)
        user_info = users.get_info(openid)
        global_orders = orders.get_global_orders(user_info['uid'])
        self.render('earns.html', datas=global_orders)


class RankHandler(WebBaseHandler):
    """ 排行榜 """

    def get(self):
        rank = users.get_users_rank()
        datas = []
        for u in rank:
            if u['headimg']:
                uid_hash = utils.md5(u['uid'])
                headimg = urlparse.urljoin(constants.SITE_BASEURL, 'static/headimg/%s/%s/%s.png' \
                                    % (uid_hash[0:2], uid_hash[2:4], u['headimg']))
            else:
                headimg = urlparse.urljoin(constants.SITE_BASEURL, 'static/img/headimg.jpg')
            tmp = {
                'name': u['name'],
                'headimg': headimg,
                'total_points': u['total_points']
            }
            datas.append(tmp)
        self.render('rank.html', datas=datas)
