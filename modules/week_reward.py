#!/usr/bin/env python
# -*- coding: utf-8 -*-
from models import week_user,users,options
def task_week_prorata(user_info,points):
    invite_by_info = users.get_info_by_uid(user_info['invite_by'])
    uid = invite_by_info['uid']
    if not week_user.check_in(uid):
        return
    invite_prorata = options.get('invite_prorata')
    invite_week_user = week_user.get_info(uid)
    invite_prize = points * invite_prorata / 100
    week_user.inc_points(invite_week_user,invite_prize)
