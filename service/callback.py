#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author zhenyong

from __future__ import division
import utils
import constants
import json

from models import users, orders
from modules import reward,week_reward
from protocols import WebBaseHandler

CALLBACK_PUSH_QUEUE = 'you1000_wechat_push_queue'


class CallbackHandler(WebBaseHandler):
    """响应广告平台积分确认响应"""

    def get(self, platform):
        log_path = self.config['log']['callback_log']
        utils.print_log('callback', log_path, self.request.uri)

        params = {}
        if platform == 'youmiios':
            self.platform = 1
            params['sign'] = self.get_argument('sign','')
            sign = self.check_sign_ios()
        elif platform == 'youmiaos':
            self.platform = 2
            params['sign'] = self.get_argument('sig','')
            sign = self.check_sign_aos()
        else:
            self.write('what the fuck?')

        keys = ['order', 'ad', 'adid', 'user', 'points', \
                'price', 'time', 'device']
        for key in keys:
            params[key] = self.get_argument(key, '')

        if not params:
            self.write('arguments is required')
            return

        if sign != params['sign']:
            self.write('invalid sign')
            return

        self.save_order(**params)
        self.write('ok')

    def save_order(
        self, order, ad, adid, user, points, price, time, device, sign):
        """保存订单"""
        # todo 使用事务 log
        user_info = users.get_info(user)
        if not user_info:
            self.write('not user')
            return

        # 用户被邀请
        if user_info['invite_by']:
            # 完成一个任务，成为有效用户
            if user_info['first_task']:
                reward.user_register(user_info)

            reward.task_prorate(user_info, int(points))
            week_reward.task_week_prorata(user_info, int(points))

        flag = orders.callback_order_exists(order)
        if not flag:
            # Android 追加任务区分 FIXME
            oid = orders.new_global_order(
                user_info['uid'], points, user_info['points'], orders.ORDER_TYP_TASK,
                u"下载安装 %s，获得 %s 积分" % (ad, points))
            users.add_total_points(user_info, points)
            p = {
                "order": order,
                "oid": oid,
                "ad": ad,
                "adid": adid,
                "user": user_info['uid'],
                "points": points,
                "price": price,
                "device": device,
                "sig": sign,
                "platform": self.platform,
            }
            msg = u"恭喜，您下载安装 %s，已成功获得 %s 积分" % (ad, points)
            self.callback_push(user, msg)
            orders.new_callback_order(p)

    def check_sign_ios(self):
        """ ios验证签名 """
        args = self.request.arguments
        kv = []
        for key in args:
            if key != 'sign':
                value = args[key][0].decode('utf-8')
                kv.append('%s=%s' % (key, value))
        raw_str = ''
        for s in sorted(kv):
            raw_str += s
        raw_str += constants.IOS_SERVER_KEY
        return utils.md5(raw_str)

    def check_sign_aos(self):
        """ aos验证签名 """
        raw_param = [constants.AOS_SERVER_KEY]
        keys = ['order', 'app', 'user', 'chn', 'ad', 'points']
        for key in keys:
            value = self.get_argument(key, '')
            raw_param.append(value)
        raw_str = '||'.join(raw_param)
        return utils.md5(raw_str)[12:20]

    def callback_push(self, openid, msg):
        self.redis.rpush(
            CALLBACK_PUSH_QUEUE,
            json.dumps({'openid': openid, 'msg': msg}))
