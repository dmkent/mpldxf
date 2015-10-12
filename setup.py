#!/usr/bin/env python
"""Setup file for the mpldxf package.

Copyright (C) 2014 David M Kent

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
    url='https://github.com/dmkent/mpldxf',
    download_url='https://github.com/dmkent/mpldxf',
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
