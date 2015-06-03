#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author cairuitao@gmail.com
#
""" 主要逻辑 """

import torndb
import server
import redis
import db

from protocols import WebBaseHandler
from service import wechat, more, applist, callback, duiba, user, invite, donate, weekaction

try:
    import __pypy__
except ImportError:
    __pypy__ = None


class Application(server.Application):

    def startup(self):
        """处理各种数据库链接等

        比如:
            self.db = torndb.Connection(
                host=self.config.mysql_host,
                database=self.config.mysql_database,
                user=self.config.mysql_user,
                password=self.config.mysql_password)
        """
        self.db = db.mysql = torndb.Connection(**self.config['mysql'])
        pool = redis.ConnectionPool(**self.config['redis'])
        self.redis = db.redis = redis.Redis(connection_pool=pool)

class MainHandler(WebBaseHandler):

    def get(self):
        self.write("hello world!")


class TestHandler(WebBaseHandler):
    """ 测试 """

    def get(self):
        self.render('goandroid.html');


if __name__ == '__main__':

    handlers = [
        (r"/", MainHandler),

        # 微信回调
        (r"/v1/wechat", wechat.WechatHandler),
        (r"/v1/wxoauth", wechat.OAuthHandler),

        # 应用列表
        (r"/v1/applist/golist", applist.GoListHandler),
        (r"/v1/applist/goandroid", applist.GoAndroidHandler),

        # 用户信息
        (r"/v1/user/info", user.MyInfoHandler),
        (r"/v1/user/record", user.MyRecordHandler),
        (r"/v1/user/rank", user.RankHandler),

        # 静态页面
        (r"/v1/more/about", more.AboutHandler),
        (r"/v1/more/help", more.HelpHandler),
        (r"/v1/more/question", more.QuestionHandler),
        (r"/v1/more/contact", more.ContactHandler),

        # 兑吧相关
        (r"/v1/duiba/points", duiba.PointsHandler),
        (r"/v1/duiba/consume", duiba.ConsumeHandler),
        (r"/v1/duiba/notify", duiba.NotifyHandler),

        # 捐款
        (r"/v1/donate/share", donate.DonateShareHandler),
        (r"/v1/donate/page", donate.DonatePageHandler),
        (r"/v1/donate/action", donate.DonateActionHandler),

        # 广告回调
        (r"/v1/callback/([^/]+)", callback.CallbackHandler),

        # 邀请推广相关
        (r"/p/([^/]+)", invite.InviteClickHandler),
        (r"/w/([^/]+)", invite.InvitePromoteHandler),

        #周活动链接
        (r"/weekaction",weekaction.WeekactionHandler),
        (r"/weekaction/iv",weekaction.WeekInviteHandler),
        # test
        (r"/test", wechat.TestHandler),
    ]

    if __pypy__:
        print("Running in PYPY")
    else:
        print("Running in CPython")

    server.mainloop(Application(handlers))
