#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#
# Copyright Youmi 2014
#
# @author chenjiehua@youmi.net
#
""" 兑吧查询接口 """
import constants
import utils
import IP
from protocols import WebBaseHandler
from modules import restrict
from models import users, orders


def check_params(params, appKey, appSecret):
    if params['appKey'] != appKey:
        return False, constants.ERR_KEY_NOT_MATCH
    if params['timestamp'] == '':
        return False, constants.ERR_TIME_NOT_NULL
    params['appSecret'] = appSecret
    sign = params.pop('sign')
    check_sign = utils.md5_sign(params)
    if sign != check_sign:
        return False, constants.ERR_INVALID_SIGN

    return True, ''


class PointsHandler(WebBaseHandler):
    """ 用户余额查询 """
    def get(self):
        log_path = self.config['log']['duiba_log']
        utils.print_log('duiba', log_path, self.request.uri)
        self.appKey = self.config['duiba']['appKey']
        self.appSecret = self.config['duiba']['appSecret']

        self.params = {}
        kv = self.request.arguments
        for k in kv:
            self.params[k] = kv[k][0].decode('utf-8')

        success, msg = check_params(self.params, self.appKey, self.appSecret)
        if not success:
            self.write_json({"status": "fail", "errorMessage": msg[1]})
            return

        user_info = users.get_info_by_uid(self.params['uid'])

        self.write_json({"status": "ok", "message": "查询成功", \
                         "data":{"credits": user_info['points']}})


class ConsumeHandler(WebBaseHandler):
    """ 积分消耗 """
    def get(self):
        log_path = self.config['log']['duiba_log']
        utils.print_log('duiba', log_path, self.request.uri)
        self.appKey = self.config['duiba']['appKey']
        self.appSecret = self.config['duiba']['appSecret']

        self.params = {}
        kv = self.request.arguments
        for k in kv:
            self.params[k] = kv[k][0].decode('utf-8')

        # 兑换地址
        self.address = ''
        for add in ['alipay', 'phone', 'qq']:
            if self.params[add]:
                if add == 'alipay':
                    self.params[add] = self.params[add].split(':')[0]
                self.address = self.params[add]

        self.user_info = users.get_info_by_uid(self.params['uid'])

        success, msg = check_params(self.params, self.appKey, self.appSecret)
        success, msg = self.__check_valid()
        if not success:
            self.write_json({"status": "fail", "message": "", "errorMessage": msg[1]})
            return

        # 全局订单
        oid = orders.new_global_order(
            self.user_info['uid'], -int(self.params['credits']), self.user_info['points'],
            orders.ORDER_TYP_EXCHANGE, self.params['description'])
        if self.params['type'] == 'coupon' or self.params['type'] == 'object':
            description = self.params['description']
        else:
            description = ''.join(self.params['description'].split(' ')[1:])
        ip_address = IP.find(self.params['ip']) if self.params['ip'] else None
        self.params['facePrice'] = int(self.params['facePrice']) / 100.0
        self.params['actualPrice'] = int(self.params['actualPrice']) / 100.0
        p = {
            'uid': self.user_info['uid'],
            'oid': oid,
            'ip': self.params['ip'],
            'ip_address': ip_address,
            'points': self.params['credits'],
            'total_points': self.params['credits'],
            'price': self.params['facePrice'],
            'total_price': self.params['actualPrice'],
            'goods_id': 0,
            'goods_title': description,
            'count': 1,
            'status': 10,
            'address_type': 0,
            'address': self.address,
            'notes': self.params['description'],
            'orderNum': self.params['orderNum'],
            'type': self.params['type'],
        }
        orders.new_exchange_order(p)
        users.sub_exchange_points(self.user_info, int(self.params['credits']))

        self.write_json({"status": "ok", "message": "查询成功", \
                         "data":{"bizId": str(oid)}})

    def __check_valid(self):
        # 检查用户状态
        success, msg = True, None
        if self.user_info['status'] in [-1, -2]:
            success, msg = False, constants.ERR_INVALID_USER
        # 检查用户积分
        if self.user_info['points'] < int(self.params['credits']):
            success, msg = False, constants.ERR_NOT_ENOUGH_POINTS
        # 兑换地址非空，需进行验证
        if self.address:
            # address对应uid数限制
            valid = restrict.valid_address_uid(self.address, self.user_info['uid'])
            if not valid:
                success, msg = False, constants.ERR_INVALID_ADDRESS
            # address每天最多兑换次数
            valid = restrict.valid_address_day(self.address)
            if not valid:
                success, msg = False, constants.ERR_EXCHANGE_MUCH

        return success, msg


class NotifyHandler(WebBaseHandler):
    """ 兑换结果通知 """
    def get(self):
        log_path = self.config['log']['duiba_log']
        utils.print_log('duiba', log_path, self.request.uri)
        self.appKey = self.config['duiba']['appKey']
        self.appSecret = self.config['duiba']['appSecret']

        self.params = {}
        kv = self.request.arguments
        for k in kv:
            self.params[k] = kv[k][0].decode('utf-8')

        success, msg = check_params(self.params, self.appKey, self.appSecret)
        if not success:
            self.write_json({"status": "false", "errorMessage": msg[1]})
            return

        order = orders.get_exchange_order(self.params['bizId'])
        # 订单不存在
        debug_path = self.config['log']['debug_log']
        if not order:
            utils.print_log('debug', debug_path, self.params['bizId'])
            return
        # 标记为拒绝的订单无需修改状态
        if order['status'] in [12, 13, 14]:
            utils.print_log('debug', debug_path, '%s-%s' % (self.params['bizId'], order['status']))
            return

        if self.params['success'].lower() == 'false':
            orders.set_order_status(self.params['bizId'],
                orders.ORDER_STS_DUI_FAIL, self.params['errorMessage'])
            # 兑换失败，退回积分，增加流水
            user_info = users.get_info_by_uid(order['uid'])
            users.add_exchange_points(user_info, order['points'])
            orders.new_global_order(
                order['uid'], order['points'], user_info['points'], orders.ORDER_TYP_EXCHANGE,
                u"兑换失败，退回 %d 钻石" % order['points'])
        elif self.params['success'].lower() == 'true':
            notes = self.params['errorMessage'] if self.params['errorMessage'] else order['notes']
            orders.set_order_status(self.params['bizId'], orders.ORDER_STS_DUI_SUCC, notes)
        else:
            self.write_json({"status": "false", "errorMessage": "code error"})
            return

        self.write('ok')
