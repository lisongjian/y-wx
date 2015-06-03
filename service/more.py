#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

微信相关
@author chenzejie

"""

import protocols



class AboutHandler(protocols.BaseHandler):
    """ 微信更多信息 """

    # 验证方法
    def get(self):
        self.render("more/about.html")


class HelpHandler(protocols.BaseHandler):
    """ 微信更多信息 """

    # 验证方法
    def get(self):
        self.render("more/help.html")


class QuestionHandler(protocols.BaseHandler):
    """ 微信更多信息 """

    # 验证方法
    def get(self):
        self.render("more/question.html")


class ContactHandler(protocols.BaseHandler):
    """ 微信更多信息 """

    # 验证方法
    def get(self):
        self.render("more/contact.html")

