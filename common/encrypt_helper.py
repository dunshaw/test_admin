 #coding:utf-8

import base64
import os
from hmac import HMAC
import hashlib, time

class Encrypt_Helper(object):
    def __init__(self):
        self.PBKDF2_ITERATIONS = 1000
        self.SALT_BYTE_SIZE = 24
        self.HASH_BYTE_SIZE = 24

    def create_hash(self,password):
        pass

    def get_salt(self):
        salt = os.urandom(self.SALT_BYTE_SIZE)
        salt = base64.b64encode(salt).decode("utf-8")
        return salt

    def makeSessionId(self,st):
        m = hashlib.md5()
        m.update('this is a test of the emergency broadcasting system'.encode('ascii'))
        m.update(str(time.time()).encode('ascii'))
        m.update(str(st).encode('ascii'))
        return m.hexdigest()

    def makeSessionId_nostring(self,st):
        
        m = hashlib.md5()
        m.update('this is a test of the emergency broadcasting system'.encode('utf-8'))
        m.update(str(time.time()).encode('utf-8'))
        m.update(str(st).encode('utf-8'))
        return m.hexdigest()

if __name__ == '__main__':
    print(Encrypt_Helper().makeSessionId(22))
    print(Encrypt_Helper().makeSessionId_nostring('thcpc'))