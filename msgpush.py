#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Youmi
#
# @author chenjiehua@youmi.net
#

import yaml
import utils
import constants
import redis
import requests
from utils import YamlLoader
from service import callback, wechat

try:
    import ujson as json
except ImportError:
    import json

SETTINGS_FILE = "settings.yaml"

def main():
    try:
        config = yaml.load(file(SETTINGS_FILE, 'r'), YamlLoader)
    except yaml.YAMLError as e:
        print "Error in configuration file: %s" % e

    log_path = config['log']['msgpush_log']
    pool = redis.ConnectionPool(**config['redis'])
    r = redis.Redis(connection_pool=pool)

    while True:
        push_raw = r.blpop(callback.CALLBACK_PUSH_QUEUE)
        if not push_raw:
            continue
        push_info = json.loads(push_raw[1])
        openid = push_info['openid']
        msg = push_info['msg']
        access_token = get_acess_token(r)
        url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s' \
            % access_token
        payload = '{"touser": "%s", "msgtype": "text", "text": {"content": "%s" }}' % (openid, msg)
        requests.post(url, data=payload.encode('utf-8'))
        info = '%s - %s' % (openid, msg)
        utils.print_log('msgpush', log_path, info)

def get_acess_token(r):
    """ 获取access_token """
    token = r.get(wechat.WX_ACCESS_TOKEN)
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
        token = None
    else:
        token = result.get('access_token', None)
        if token:
            r.setex(wechat.WX_ACCESS_TOKEN, token, 7000)
    return token


if __name__ == "__main__":
    main()
