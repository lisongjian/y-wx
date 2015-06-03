#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Youmi 2014
#
# @author: chenjiehua@youmi.net
#

""" 加密解密模块 """

import base64
import urllib
import constants

from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:
    """ AES 加密解密 """

    def __init__(self, platform=1):
        self.bs = 16
        if platform == 1:
            self.key = constants.IOS_SECRET
            self.appid = constants.IOS_APPID
        else:
            self.key = constants.AOS_SECRET
            self.appid = constants.AOS_APPID

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def encode(self, openid):
        return urllib.quote_plus(self.appid + self.encrypt(openid))
