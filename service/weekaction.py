#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urlparse
import constants
from models import week_user,users
from protocols import WebBaseHandler
import autoAccount
class WeekactionHandler(WebBaseHandler):

    def get(self):
        self.uid = self.get_argument('uid',None)
        flag = autoAccount.check_valid_date()
        if flag == 1:
            self.write("活动过期,期待新的开始吧!")
            return
        elif flag == -1:
            self.write("亲~新活动即将开始哦！")
            return
        if  week_user.check_in(self.uid):
            self.show_week_account(self.uid)
            return
        self.render('act1/desc.html',uid=self.uid)

    def post(self):
        self.uid = self.get_argument('uid',None)
        if not week_user.check_in(self.uid):
       	    week_user.new_user(self.uid)
        self.show_week_account(self.uid)

    def show_week_account(self,uid):
	user_info=week_user.get_info(uid)
	if not user_info:
     	     return
	prize,grade,next_stage = autoAccount.get_prize_grade_next_stage(user_info['week_points'])
	if grade == None:
	     grade='无'
	if next_stage != None:
   	     next_stag = next_stage - user_info['week_points']+1
	else:
	     next_stag=0
        self.render('act1/check.html',uid=uid,points=user_info['week_points'],prize=prize,next_stage=next_stag,grade=grade)
	return

class WeekInviteHandler(WebBaseHandler):
    def get(self):
        uid = self.get_argument('uid',None)
        if not uid:
            return
        user_info = users.get_info_by_uid(uid)
        if not user_info:
            return
        url = urlparse.urljoin(constants.SITE_BASEURL, '/p/%s' % user_info['openid'])
        self.redirect(url)

