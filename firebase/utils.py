# -*- coding: utf-8 -*-
import requests
import datetime
import json
import decimal

from functools import wraps


def connect(timeout):
    def wrapper(f):
        def wrapped(*args, **kwargs):
            if 'connection' in kwargs and kwargs['connection']:
                connection = kwargs['connection']
            else:
                connection = requests.Session()
                kwargs['connection'] = connection
            connection.timeout = timeout
            connection.headers.update(
                {'Content-type': 'application/json'}
            )
            return f(*args, **kwargs)
        return wraps(f)(wrapped)
    return wrapper


class InstanceForematter(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return seconds_formatter(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)


def seconds_formatter(obj):
    return ((obj.days * 86400 + obj.seconds) * 10 ** 6 + obj.microseconds) \
           / 10 ** 6.0


@connect(60)
def make_get_request(url, params, headers, connection):
    timeout = getattr(connection, 'timeout')
    response = connection.get(url, params=params,
                              headers=headers, timeout=timeout)
    if response.ok or response.status_code == 403:
        return response.json() if response.content else None
    else:
        response.raise_for_status()


@connect(60)
def make_put_request(url, data, params, headers, connection):
    timeout = getattr(connection, 'timeout')
    response = connection.put(url, data=data, params=params, headers=headers,
                              timeout=timeout)
    if response.ok or response.status_code == 403:
        return response.json() if response.content else None
    else:
        response.raise_for_status()


@connect(60)
def make_post_request(url, data, params, headers, connection):
    timeout = getattr(connection, 'timeout')
    response = connection.post(url, data=data, params=params, headers=headers,
                               timeout=timeout)
    if response.ok or response.status_code == 403:
        return response.json() if response.content else None
    else:
        response.raise_for_status()


@connect(60)
def make_patch_request(url, data, params, headers, connection):
    timeout = getattr(connection, 'timeout')
    response = connection.patch(url, data=data, params=params, headers=headers,
                                timeout=timeout)
    if response.ok or response.status_code == 403:
        return response.json() if response.content else None
    else:
        response.raise_for_status()


@connect(60)
def make_delete_request(url, params, headers, connection):
    timeout = getattr(connection, 'timeout')
    response = connection.delete(url, params=params,
                                 headers=headers, timeout=timeout)
    if response.ok or response.status_code == 403:
        return response.json() if response.content else None
    else:
        response.raise_for_status()


class ImportDjangoError(Exception):
    def __str__(self):
        return u"Cannot import django's conf module and storage module. " \
               u"Check your django path."
