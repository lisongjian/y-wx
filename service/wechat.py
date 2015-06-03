#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信相关
@author chenzejie

"""

from __future__ import division
import constants
import urlparse
import requests
import os
import re
import time
import utils

from PIL import Image
from StringIO import StringIO
from protocols import WechatBaseHandler, WebBaseHandler
from models import users
from crypt import AESCipher


WX_ACCESS_TOKEN = 'you1000_wechat_access_token'

class WechatHandler(WechatBaseHandler):
    """ 微信消息处理 """

    user_info = None
    openid = None
    r = None

    # 验证方法
    def get(self):
        sign = self.get_sign()
        valid = self.check_signautre(sign)
        if valid:
            self.write(sign['echostr'])
        else:
            self.write('sign wrong')

    # 正常与微信交互
    def post(self):
        sign = self.get_sign()
        valid = self.check_signautre(sign)
        if valid:
            msg_xml = self.request.body
            self.handle_msg(msg_xml)

    def handle_msg(self, msg_xml):
        msg = self.parse_from_xml(msg_xml)
        msg_type = msg.get('MsgType', None)
        self.openid = msg.get('FromUserName', '')
        self.r = utils.encrypt(self.openid)
        self.user_info = users.get_info(self.openid)
        if not self.user_info:
            self.new_user()
            self.user_info = users.get_info(self.openid)
        elif self.user_info['status'] == -1:
            users.set_status(self.openid, 0)

        reply = None
        if msg_type == 'text':
            # 文本信息处理
            reply = self.text_handler(msg)
        elif msg_type == 'event':
            # 事件信息处理
            reply = self.event_handler(msg)
        else:
            # 其他类型消息
            pass
        if reply:
            self.write(reply)

    def new_user(self):
        """ 获取用户信息 """
        token = self.get_access_token()
        url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        params = {
            'access_token': token,
            'openid': self.openid,
            'lang': 'zh_CN',
        }
        req = requests.get(url, params=params)
        result = req.json()
        if result.get('errcode', None):
            self.redis.delete(WX_ACCESS_TOKEN)
            return None
        # 用户是否被邀请
        invite_by = self.__check_invite(result['openid'])
        # name参数存在emoji字符
        ma = re.compile(u'[\U00010000-\U0010ffff]')
        nickname = ma.sub(u'', result['nickname'])
        info = {
            'openid':result['openid'],
            'name': nickname,
            'sex': result['sex'],
            'city': result['city'],
            'country': result['country'],
            'province': result['province'],
            'invite_by': invite_by,
        }
        uid = users.new_user(**info)
        # 用户头像是否存在
        if result.get('headimgurl', None):
            headimg = self.save_headimg(result['headimgurl'], uid)
            users.set_headimg(uid, headimg)
        return uid

    def __check_invite(self, openid):
        """ 检查用户是否被邀请 """
        key_name = 'you1000_wechat_invite_%s' % openid
        openid = self.redis.get(key_name)
        if openid:
            user_info = users.get_info(openid)
            return user_info['uid']
        else:
            return 0

    def save_headimg(self, url, uid):
        """ 抓取用户头像 """
        uid_hash = utils.md5(str(uid))
        uid_base62 = utils.base62_encode(uid)
        path = 'headimg/%s/%s' % (uid_hash[0:2], uid_hash[2:4])
        path = os.path.join(constants.STATIC_DIR, path)
        try:
            os.makedirs(path)
        except OSError:
            pass
        img_path = os.path.join(path, '%s.png' % uid_base62)
        url = url[:-1] + '132'
        req = requests.get(url)
        im = Image.open(StringIO(req.content))
        im.save(img_path, "PNG")
        return uid_base62

    def get_access_token(self):
        """ 获取access_token """
        token = self.redis.get(WX_ACCESS_TOKEN)
        if token:
            return token

        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'grant_type': 'client_credential',
            'appid': constants.WX_APPID,
            'secret': constants.WX_SECRET,
        }
        req = requests.get(url, params=params)
        result = req.json()
        if result.get('errcode', None):
            self.write(req.text)
            token = None
        else:
            token = result.get('access_token', None)
            if token:
                self.redis.setex(WX_ACCESS_TOKEN, token, 7000)

        return token

    def text_handler(self, msg):
        """ 文本回调 """
        content = msg.get('Content', '')
        if 'iloveumlife' == content:
            aes = AESCipher(2)
            r = aes.encode(self.openid)
            url = 'http://w.ymapp.com/wx/aos/lists.html?r=%s' % r
            tt = '<a href="%s">传送门</a>' % url
            resp_content = self.parse_to_xml(msg, tt)
        else:
            resp_content = self.show_faq(msg)
        return resp_content

    def event_handler(self, msg):
        """ 事件回调 """
        resp_content = None
        event = msg.get('Event', '')

        if event == 'subscribe':
            # 关注
            resp_content = self.show_welcome(msg)
        elif event == 'unsubscribe':
            # 取消关注
            users.set_status(self.openid, -1)
        elif event == 'SCAN':
            pass
        elif event == 'CLICK':
            # 点击菜单
            resp_content = self.click_handler(msg)

        return resp_content

    def click_handler(self, msg):
        """ 点击事件回调 """
        event_key = msg.get('EventKey', '')
        echostr = ''

        if event_key == 'trylist':
            pass

        elif event_key == 'invite':
            echostr = self.show_invite(msg)

        elif event_key == 'record':
            pass

        elif event_key == 'info':
            pass

        elif event_key == 'duiba':
            pass
            #duiba_url = self.duiba_login()
            #echotpl =  '亲爱的小伙伴！\r\n您的辛勤劳动给您带来了%s积分！\r\n<a href="%s">点击这里,兑换积分</a>' \
            #    % (self.user_info['points'], duiba_url)
            #echostr = self.parse_to_xml(msg, echotpl)

        elif event_key == 'contact':
            echotpl =  '客服QQ: 670954550\r\n官方QQ群: <a href="http://shang.qq.com/wpa/qunwpa?idkey=c40be90f4449954a662c8434747f34580ba2a04a399d99bc88299751f7e725f8">366524869</a>'
            echostr = self.parse_to_xml(msg, echotpl)

	elif event_key == 'weekaction':
            self.user_info = users.get_info(self.openid)
	    echostr = self.show_weekaction(msg,self.user_info['uid'])
        else:
            pass

        return echostr

    def show_invite(self, msg):
        """ 以图文形式返回邀请规则 """
        url = urlparse.urljoin(constants.SITE_BASEURL, 'p/%s' % self.openid)
        pic_url = urlparse.urljoin(constants.SITE_BASEURL, 'static/img/invite.png')
        item = {
            'title': '每成功邀请一个好友就给1元！',
            'description': '邀请您的好友加入应用体验师，每成功邀请一个朋友，您都可以获得1元的现金奖励！另外，好友做任务还有分成哦～～～掐指一算，邀请1000名好友就可获得几千元奖励哦！',
            'pic_url': pic_url,
            'url': url
        }
        items = []
        items.append(item)
        echostr = self.parse_to_xml_news(msg, items)
        return echostr

    def show_welcome(self, msg):
        """ 以图文形式返回积分墙的地址 """
        r = utils.encrypt(self.openid)
        url = urlparse.urljoin(constants.SITE_BASEURL, 'v1/applist/golist?r=%s' % r)
        pic_url = urlparse.urljoin(constants.SITE_BASEURL, 'static/img/list.png')
        item = {
            'title': '应用体验师，抢先试玩应用',
            'description': '嗨 %s，你真厉害！这么快就关注到我们的微信号，比别人抢先很多步哦！试玩应用，即可获得Q币、话费，支付宝。你，将是一名神圣的“应用体验师”！ 开始体验之旅！' % self.user_info['name'],
            'pic_url': pic_url,
            'url': url
        }
        items = []
        items.append(item)
        echostr = self.parse_to_xml_news(msg, items)
        return echostr

    def show_faq(self, msg):
        """ 以图文形式返回FAQ """
        url = 'http://mp.weixin.qq.com/s?__biz=MzAwNzAzMTQxOA==&mid=201580815&idx=1&sn=9879bd910435e2c4582b7466783e477c#rd'
        pic_url = urlparse.urljoin(constants.SITE_BASEURL, 'static/img/faq.jpg')
        item = {
            'title': '问答集锦，有疑问戳这里，体验师教你赚钱，陪你任性！',
            'description': '体验师小助手，为神马我做了任务却没有积分？！全民反馈被我手抖删了肿么办啊？为神马我的订单会兑换失败呢？为神马@￥%#！~&%￥&#@……小伙伴们如果有什么疑问，请直接猛戳这里，总有一款会是你的菜！体验师教你赚钱，陪你任性！',
            'pic_url': pic_url,
            'url': url
        }
        items = []
        items.append(item)
        echostr = self.parse_to_xml_news(msg, items)
        return echostr

    def show_weekaction(self,msg,uid):
        """ 返回活动"""
        url = urlparse.urljoin(constants.SITE_BASEURL, 'weekaction?uid=%s' % uid)
        pic_url = urlparse.urljoin(constants.SITE_BASEURL, 'static/img/act_title.png')
        item ={
            'title':'take it easy',
            'description':'I am a test man',
            'pic_url' : pic_url,
            'url':    url
        }
        items = []
        items.append(item)
        echostr = self.parse_to_xml_news(msg,items)
        return echostr


class OAuthHandler(WebBaseHandler):
    """ 微信OAuth回调 """

    def get(self):
        code = self.get_argument('code', None)
        stat = self.get_argument('state', None)
        if not code or not stat:
            self.write('跳转失败，请重试')
            return

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
            self.write(r.text)
            return

        r = utils.encrypt(result['openid'])
        if stat == 'applist':
            target_url = 'v1/applist/golist?r=%s' % r
        elif stat == 'info':
            target_url = 'v1/user/info?r=%s' % r
        elif stat == 'record':
            target_url = 'v1/user/record?r=%s' % r
        elif stat == 'weekaction':
            user_info = users.get_info(result['openid'])
            target_url = 'weekaction?uid=%s' % user_info['uid']
        elif stat == 'duiba':
            self.user_info = users.get_info(result['openid'])
            url = self.duiba_login()
            self.redirect(url, False, 302)
            return

        url = urlparse.urljoin(constants.SITE_BASEURL, target_url)
        self.redirect(url, False, 302)

    def duiba_login(self):
        # 兑吧登陆
        timestamp = int(time.time() * 1000)
        uid = self.user_info['uid']
        points = self.user_info['points']
        appKey = self.config['duiba']['appKey']
        appSecret = self.config['duiba']['appSecret']
        params = {
            'uid': uid,
            'credits': points,
            'appSecret': appSecret,
            'appKey': appKey,
            'timestamp': timestamp,
        }
        sign = utils.md5_sign(params)
        url = "http://www.duiba.com.cn/autoLogin/autologin?uid=%s&credits=%s&appKey=%s&sign=%s&timestamp=%s" \
            % (uid, points, appKey, sign, timestamp)
        return url


class TestHandler(WechatBaseHandler):
    def get(self):
        self.user_info = {
            "uid": 10007,
            "points": 123456,
        }
        print self.duiba_login()
        #all_users = self.db.query("SELECT * FROM `users`")
        #for user in all_users:
        #    self.deal_user(user['openid'], user['uid'])
        #    break

    def duiba_login(self):
        # 兑吧登陆
        timestamp = int(time.time() * 1000)
        uid = self.user_info['uid']
        points = self.user_info['points']
        appKey = self.config['duiba']['appKey']
        appSecret = self.config['duiba']['appSecret']
        params = {
            'uid': uid,
            'credits': points,
            'appSecret': appSecret,
            'appKey': appKey,
            'timestamp': timestamp,
        }
        sign = utils.md5_sign(params)
        url = "http://www.duiba.com.cn/autoLogin/autologin?uid=%s&credits=%s&appKey=%s&sign=%s&timestamp=%s" \
            % (uid, points, appKey, sign, timestamp)
        return url

    def deal_user(self, openid, uid):
        """ 获取用户信息 """
        token = self.get_access_token()
        url = 'https://api.weixin.qq.com/cgi-bin/user/info'
        params = {
            'access_token': token,
            'openid': openid,
            'lang': 'zh_CN',
        }
        req = requests.get(url, params=params)
        result = req.json()
        if result.get('errcode', None):
            self.redis.delete(WX_ACCESS_TOKEN)
            return None
        if result['subscribe'] == 0:
            users.set_status(openid, -1)
            return None

        # 用户头像是否存在
        if result.get('headimgurl', None):
            self.save_headimg(result['headimgurl'], uid)
        return uid

    def save_headimg(self, url, uid):
        """ 抓取用户头像 """
        uid_hash = utils.md5(str(uid))
        uid_base62 = utils.base62_encode(uid)
        path = 'headimg/%s/%s' % (uid_hash[0:2], uid_hash[2:4])
        path = os.path.join(constants.STATIC_DIR, path)
        try:
            os.makedirs(path)
        except OSError:
            pass
        img_path = os.path.join(path, '%s.png' % uid_base62)
        url = url[:-1] + '132'
        req = requests.get(url)
        im = Image.open(StringIO(req.content))
        im.save(img_path, "PNG")
        return uid_base62

    def get_access_token(self):
        """ 获取access_token """
        token = self.redis.get(WX_ACCESS_TOKEN)
        if token:
            return token

        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'grant_type': 'client_credential',
            'appid': constants.WX_APPID,
            'secret': constants.WX_SECRET,
        }
        req = requests.get(url, params=params)
        result = req.json()
        if result.get('errcode', None):
            self.write(req.text)
            token = None
        else:
            token = result.get('access_token', None)
            if token:
                self.redis.setex(WX_ACCESS_TOKEN, token, 7000)

        return token

