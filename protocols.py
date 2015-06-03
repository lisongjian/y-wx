#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author cairuitao@gmail.com
#

""" JSON交换协议的HTTP Handler """

import tornado.web
import constants
import utils
import time

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

try:
    import ujson as json
except ImportError:
    import json

class BaseHandler(tornado.web.RequestHandler):
    """ 公共基础函数 """

    @property
    def db(self):
        return self.application.db

    @property
    def config(self):
        return self.application.config

    @property
    def redis(self):
        return self.application.redis


class WechatBaseHandler(BaseHandler):
    """ 用于Wechat使用的基础函数 """

    # 把xml转换为数组
    def parse_from_xml(self, msg_xml):
        root_elem = ET.fromstring(msg_xml)
        msg = {}
        if root_elem.tag == 'xml':
            for child in root_elem:
                msg[child.tag] = child.text
        return msg

    # 回复文本信息
    def parse_to_xml(self, msg, content):
        ext_tpl = "<xml>\
                    <ToUserName><![CDATA[%s]]></ToUserName>\
                    <FromUserName><![CDATA[%s]]></FromUserName>\
                    <CreateTime>%s</CreateTime>\
                    <MsgType><![CDATA[%s]]></MsgType>\
                    <Content><![CDATA[%s]]></Content>\
                    </xml>"
        ext_tpl = ext_tpl % (msg['FromUserName'], msg['ToUserName'],
                             str(int(time.time())), 'text', content)
        return ext_tpl

    # 回复图文信息
    def parse_to_xml_news(self, msg, items):
        openid = msg.get('FromUserName', '')
        aid = msg.get('ToUserName', '')
        ext_tpl = """<xml>
                 <ToUserName><![CDATA[%s]]></ToUserName>
                 <FromUserName><![CDATA[%s]]></FromUserName>
                 <CreateTime>%s</CreateTime>
                 <MsgType><![CDATA[%s]]></MsgType>
                 <ArticleCount>%d</ArticleCount>
                 <Articles>
                    %s
                 </Articles>
                 <FuncFlag>1</FuncFlag>
                 </xml> """
        item_xml_tpl = """<item>
                         <Title><![CDATA[%s]]></Title>
                         <Description><![CDATA[%s]]></Description>
                         <PicUrl><![CDATA[%s]]></PicUrl>
                         <Url><![CDATA[%s]]></Url>
                         </item>"""
        item_xml_list = []
        for item in items:
            item_xml = item_xml_tpl % (item['title'], item['description'],
                                       item['pic_url'], item['url'])

            item_xml_list.append(item_xml)

        items_xml = ''.join(item_xml_list)
        ext_tpl = ext_tpl % (openid, aid, str(int(time.time())), 'news', len(items), items_xml)

        return ext_tpl


    # 验证消息的真实性
    def check_signautre(self, sign):
        """ 验证消息的真实性 """
        if not sign['signature'] or not sign['timestamp'] or not sign['nonce']:
            return False

        params = [constants.TOKEN, str(sign['timestamp']), sign['nonce']]
        params.sort()
        params_str = ''.join(params)
        server_sign = utils.sha1(params_str)

        valid = False
        if server_sign == sign['signature']:
            valid = True
        return valid

    # 获取签名参数
    def get_sign(self):
        """ 获取签名参数 """
        keys = ['signature', 'timestamp', 'nonce', 'echostr']
        sign = {}
        for key in keys:
            sign[key] = self.get_argument(key, '')
        return sign


class WebBaseHandler(BaseHandler):
    """ 用于Web页面使用的基础函数 """

    def write_json(self, response=None):
        self.set_header('Content-type', 'application/json; charset=UTF-8')
        self.write(json.dumps(response))
