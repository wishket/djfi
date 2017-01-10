# -*- coding:utf-8 -*-

import urlparse

from .token import TokenGenerator
from .utils import *

try:
    from django.conf import settings
except ImportError:
    raise ImportDjangoError

__all__ = ['FirebaseAuthentication', 'FirebaseApplication']


# This Project is changed for django from python-firebase
# Main change purpose is using django.settings


class FirebaseUser(object):
    def __init__(self, email, auth_token, provider, id=None):
        self.email = email
        self.auth_token = auth_token
        self.provider = provider
        self.id = id


class FirebaseAuthentication(object):
    def __init__(self, debug=False, admin=False, extra=None):
        secret = settings.FIREBASE_SECRET_KEY
        email = settings.FIREBASE_EMAIL
        self.authenticator = TokenGenerator(secret, debug, admin)
        self.email = email
        self.provider = 'password'
        self.extra = (extra or {}).copy()
        self.extra.update({'debug': debug, 'admin': admin,
                           'email': self.email, 'provider': self.provider})

    def get_user(self):
        token = self.authenticator.create_token(self.extra)
        user_id = self.extra.get('id')
        return FirebaseUser(self.email, token, self.provider, user_id)


class FirebaseInit(object):
    NAME_EXTENSION = '.json'
    URL_SEPERATOR = '/'
    dsn = settings.FIREBASE_DOMAIN

    def __init__(self, authentication=None):
        assert self.dsn.startswith('https://'), 'DSN must be a secure URL'
        self.dsn = self.dsn
        self.authentication = authentication

    def _build_endpoint_url(self, url, name=None):
        if not url.endswith(self.URL_SEPERATOR):
            url += self.URL_SEPERATOR
        if name is None:
            name = ''
        return '%s%s%s' % (urlparse.urljoin(self.dsn, url), name,
                           self.NAME_EXTENSION)

    def _authenticate(self, params, headers):
        if self.authentication:
            user = self.authentication.get_user()
            params.update({'auth': user.firebase_auth_token})
            headers.update(self.authentication.authenticator.HEADERS)

    @connect(60)
    def get(self, url, name, params=None, headers=None, connection=None):
        name = None if name is None else name
        params = params or {}
        headers = headers or {}
        endpoint = self._build_endpoint_url(url, name)
        self._authenticate(params, headers)
        return make_get_request(endpoint, params, headers, connection=connection)

    @connect(60)
    def put(self, url, name, data, params=None, headers=None, connection=None):
        assert name, 'Snapshot name must be specified'
        params = params or {}
        headers = headers or {}
        endpoint = self._build_endpoint_url(url, name)
        self._authenticate(params, headers)
        data = json.dumps(data, cls=InstanceForematter)
        return make_put_request(endpoint, data, params, headers,
                                connection=connection)

    @connect(60)
    def post(self, url, data, params=None, headers=None, connection=None):
        params = params or {}
        headers = headers or {}
        endpoint = self._build_endpoint_url(url, None)
        self._authenticate(params, headers)
        data = json.dumps(data, cls=InstanceForematter)
        return make_post_request(endpoint, data, params, headers,
                                 connection=connection)

    @connect(60)
    def patch(self, url, data, params=None, headers=None, connection=None):
        params = params or {}
        headers = headers or {}
        endpoint = self._build_endpoint_url(url, None)
        self._authenticate(params, headers)
        data = json.dumps(data, cls=InstanceForematter)
        return make_patch_request(endpoint, data, params, headers,
                                  connection=connection)

    @connect(60)
    def delete(self, url, name, params=None, headers=None, connection=None):
        if not name: name = ''
        params = params or {}
        headers = headers or {}
        endpoint = self._build_endpoint_url(url, name)
        self._authenticate(params, headers)
        return make_delete_request(endpoint, params, headers, connection=connection)
