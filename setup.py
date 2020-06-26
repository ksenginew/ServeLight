#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup  # noqa, analysis:ignore
except ImportError:
    print ('''please install setuptools
python -m pip install setuptools
or
python -m pip install setuptools''')
    raise ImportError()

from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

## Setup

setup(
    name='ServeLight',
    version='3.1.2',
    author='Kavindu Santhusa',
    author_email='kavindusanthusa@gmail.com',
    license='MIT',
    url='https://github.com/Ksengine/ServeLight',
    download_url='https://pypi.python.org/pypi/ServeLight',
    keywords='simple, lightweight, WSGI, micro, server, library, python'
        ,
    description='Lightweight and Responsive Server Framework'
        ,
    long_description=long_description,
    long_description_content_type='text/markdown',
    platforms='any',
    packages=["sl"],
    zip_safe=True,
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3',
        ],
    include_package_data=True,
    )
