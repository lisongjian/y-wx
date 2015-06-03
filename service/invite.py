#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

import requests
import urllib
import constants
import urlparse

from protocols import WebBaseHandler

INVITE_CACHE_TIME = 60*60*24*7


class InviteClickHandler(WebBaseHandler):
    """ 用户点击邀请分享链接 """

    def get(self, openid):
        if not openid:
            openid = 'oeqg7s3h1R0300KXCMCff0BsyrHU'

        code = self.get_argument('code', None)
        if not code:
            redirect_uri = urllib.quote_plus(urlparse.urljoin(constants.SITE_BASEURL, 'p/%s' % openid))
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
            url = urlparse.urljoin(constants.SITE_BASEURL, 'p/%s' % openid)
            self.redirect(url)
            return

        # 判断打开分享页面的是：本人？其他用户
        if openid == result['openid']:
            who = 1
        else:
            key_name = 'you1000_wechat_invite_%s' % result['openid']
            self.redis.set(key_name, openid)
            who = 0
        datas = {
            'who': who,
            'appid': constants.WX_APPID,
            'base_url': constants.SITE_BASEURL,
            'redirect_url': urlparse.urljoin(constants.SITE_BASEURL, 'p/%s' % openid),
        }
        self.render('invite.html', datas=datas)


class InvitePromoteHandler(WebBaseHandler):
    """ 推广链接 """

    def get(self, openid):
        if not openid:
            openid = 'oeqg7s3h1R0300KXCMCff0BsyrHU'

        code = self.get_argument('code', None)
        if not code:
            redirect_uri = urllib.quote_plus(urlparse.urljoin(constants.SITE_BASEURL, 'w/%s' % openid))
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
            url = urlparse.urljoin(constants.SITE_BASEURL, 'p/%s' % openid)
            self.redirect(url)
            return

        # 判断打开分享页面的是：本人？其他用户
        if openid != result['openid']:
            key_name = 'you1000_wechat_invite_%s' % result['openid']
            self.redis.set(key_name, openid)

        article_url = 'http://mp.weixin.qq.com/s?__biz=MzAwNzAzMTQxOA==&mid=201069454&idx=1&sn=df55a306e997a6c556ad9d767abcdfd0#rd'
        self.redirect(article_url)
