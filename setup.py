# -*- coding:utf-8 -*-

from distutils.core import setup

setup(
    name='djfi',
    version='0.0.1',
    py_modules=['firebase', ],
    packages=['firebase', ],
    license='GNU GPL 3.0',

    author='yonggill',
    author_email='yonggill@wishket.com',
    description='django wrapper for Google Firebase',
    keywords=['python', 'firebase'],

    install_requires=[
        'requests'
    ]
)