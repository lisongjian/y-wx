#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# @author: jiehua233@gmail.com
#

import yaml
import os.path
import hashlib
import logging
import re
import urllib

from crypt import AESCipher
from user_agents import parse

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class YamlLoader(yaml.Loader):

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(YamlLoader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, YamlLoader)

YamlLoader.add_constructor('!include', YamlLoader.include)

alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base62_decode(string):
    """ 短地址解码 """
    base = len(alphabet)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num


def base62_encode(num):
    """ 短地址编码 """
    if num == 0:
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def md5(text):
    return hashlib.new("md5", str(text)).hexdigest()


def sha1(text):
    return hashlib.new("sha1", text).hexdigest()


def md5_sign(params):
    """ 兑吧签名验证 """
    # 排序
    def ksort(d):
        return [(k, d[k]) for k in sorted(d.keys())]

    sorted_params = ksort(params)
    raw_str = ''
    for p in sorted_params:
        raw_str += str(p[1])
    return md5(raw_str)


def print_log(log_name, log_path, info):
    """ 日志打印 """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(fh)
    logger.info(info)


def get_platform(ua_string):
    """ 根据User-Agent判断系统类型 """
    ua = parse(ua_string)
    os_family = ua.os.family
    if os_family == 'iOS':
        platform = 1
    elif os_family == 'Android':
        platform = 2
    else:
        platform = 0
    return platform


def decrypt(enc_str, platform=1):
    aes = AESCipher(platform)
    dec = aes.decrypt(urllib.unquote(enc_str))
    return dec


def encrypt(raw_str, platform=1):
    aes = AESCipher(platform)
    enc = urllib.quote(aes.encrypt(raw_str))
    return enc
