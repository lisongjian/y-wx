#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

微信相关
@author chenzejie

"""

import IP
import utils
import constants
import urlparse

from protocols import WebBaseHandler
from models import users
from crypt import AESCipher


class GoListHandler(WebBaseHandler):
    """ 跳转积分墙应用列表 """

    def get(self):
        r = self.get_argument('r', '')
        if not r:
            self.write('参数错误')
            return

        openid = utils.decrypt(r)

        user_agent = self.request.headers.get('User-Agent', '')
        platform = utils.get_platform(user_agent)
        # 判断用户系统是否已知
        user_info = users.get_info(openid)
        if not user_info['platform']:
            ip = self.request.remote_ip
            ip_address = IP.find(ip)
            users.set_ip(openid, ip, ip_address, platform)

        if user_info['status'] == -2:
            self.write("非法用户")
            return

        if platform == 2:
            url = urlparse.urljoin(constants.SITE_BASEURL, 'v1/applist/goandroid')
            self.redirect(url, False, 302)
            return

        aes = AESCipher()
        r = aes.encode(openid)
        url = 'http://w.ymapp.com/wx/ios/lists.html?r=%s' % r
        #url = 'http://au.youmi.net/wx/ios/lists.html?r=%s' % r
        self.redirect(url, False, 302)


class GoAndroidHandler(WebBaseHandler):
    """ 引导用户下载Android版全名赚钱 """

    def get(self):
        self.render('goandroid.html')
