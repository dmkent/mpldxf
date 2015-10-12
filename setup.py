#!/usr/bin/env python
"""Setup file for the mpldxf package.

Copyright (C) 2014 David M Kent

Distribution of this software without written permission of the
copyright holder is prohibited.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""

import os
from setuptools import setup

VERSION = "0.1.0"
AUTHOR_NAME = 'David Kent'
AUTHOR_EMAIL = 'davidkent@fastmail.com.au'


def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as f:
            return f.read()
    except IOError:
        return "File '%s' not found.\n" % fname

setup(
    name='mpldxf',
    version=VERSION,
    description='A matplotlib backend to write DXF drawings.',
    author=AUTHOR_NAME,
    url='http://bitbucket.org/dmkent/mpldxf',
    download_url='http://bitbucket.org/dmkent/mpldxf/downloads',
    author_email=AUTHOR_EMAIL,
    packages=['mpldxf'],
    provides=['mpldxf'],
    keywords=['matplotlib', 'DXF', 'CAD'],
    long_description=read('README.rst'),
    platforms="OS Independent",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    install_requires=[
        "ezdxf",
        "matplotlib",
    ],
    dependency_links=[
        'hg+https://bitbucket.org/mozman/ezdxf@default#egg=ezdxf-default',
    ],
)
