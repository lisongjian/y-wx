#!/usb/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author chenjiehua@youmi.net
#

from models import users, orders, options, invites

def user_register(user_info):
    users.set_first_task(user_info['uid'])
    invite_prize = options.get('invite_register')
    invite_by_info = users.get_info_by_uid(user_info['invite_by'])
    oid = orders.new_global_order(
        invite_by_info['uid'], invite_prize, invite_by_info['points'],
        orders.ORDER_TYP_REGISTER,
        u"邀请 %s 关注，获得 %s 积分" % (user_info['name'], invite_prize)
    )
    invites.new_invite(
        oid, invite_by_info['uid'], user_info['uid'], invites.INVITE_REGISTER, invite_prize)
    users.add_invite_points(invite_by_info, invite_prize)
    users.incr_invites(invite_by_info)

def task_prorate(user_info, points):
    invite_by_info = users.get_info_by_uid(user_info['invite_by'])
    invite_prorata = options.get('invite_prorata')
    invite_prize = points * invite_prorata / 100
    oid = orders.new_global_order(
        invite_by_info['uid'], invite_prize, invite_by_info['points'],
        orders.ORDER_TYP_PRORATA,
        u"邀请 %s 任务分成 %s%%，获得 %s 积分" % \
        (user_info['name'], invite_prorata, invite_prize)
    )
    invites.new_invite(
        oid, invite_by_info['uid'], user_info['uid'], invites.INVITE_PRORATA, invite_prize)
    users.add_invite_points(invite_by_info, invite_prize)

