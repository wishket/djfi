# -*- coding:utf-8 -*-

import base64
import hashlib
import hmac
import json
import time

__all__ = ['FirebaseTokenGenerator']


class TokenGenerator(object):
    TOKEN_VERSION = 0
    TOKEN_SEP = '.'
    CLAIMS_MAP = {
        'expires': 'exp',
        'notBefore': 'nbf',
        'admin': 'admin',
        'debug': 'debug',
        'simulate': 'simulate'
    }
    HEADERS = {'typ': 'JWT', 'alg': 'HS256'}

    def __init__(self, secret, debug=False, admin=False):
        assert secret, 'Your Firebase SECRET is not valid'
        self.secret = secret
        self.admin = admin
        self.debug = debug

    def create_token(self, data, options=None):
        if not options:
            options = {}
        options.update({'admin': self.admin, 'debug': self.debug})
        claims = self._create_options_claims(options)
        claims['v'] = self.TOKEN_VERSION
        claims['iat'] = int(time.mktime(time.gmtime()))
        claims['d'] = data
        return self._encode_token(self.secret, claims)

    def _create_options_claims(self, opts):
        claims = {}
        for k in opts:
            if k in self.CLAIMS_MAP:
                claims[k] = opts[k]
            else:
                raise ValueError('Unrecognized Option: %s' % k)
        return claims

    def _encode(self, bytes):
        encoded = base64.urlsafe_b64encode(bytes)
        return encoded.decode('utf-8').replace('=', '')

    def _encode_json(self, obj):
        return self._encode(json.dumps(obj).encode("utf-8"))

    def _sign(self, secret, to_sign):
        def portable_bytes(s):
            try:
                return bytes(s, 'utf-8')
            except TypeError:
                return bytes(s)
        return self._encode(hmac.new(portable_bytes(secret), portable_bytes(to_sign),
                                     hashlib.sha256).digest())

    def _encode_token(self, secret, claims):
        encoded_header = self._encode_json(self.HEADERS)
        encoded_claims = self._encode_json(claims)
        secure_bits = '%s%s%s' % (encoded_header, self.TOKEN_SEP, encoded_claims)
        sig = self._sign(secret, secure_bits)
        return '%s%s%s' % (secure_bits, self.TOKEN_SEP, sig)

