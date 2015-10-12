"""
DXF colour table tools.

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
from math import sqrt

from ezdxf.tools import rgb


# Most CAD programs seem to handle index 7 as either white or black
# depending on the drawing's background colour. To avoid this (given
# matplotlib normally draws a white background anyway) we automatically
# map black values to a very dark grey.
BLACK = 250
WHITE = 255


def _distance(target, test):
    """Get Euclidean distance between two tuples."""
    return sqrt(sum([(a - b) * (a - b) for a, b in zip(target, test)]))


def nearest_index(rgb_color):
    """Get the DXF color index for the color nearest to the RGB color."""
    distances = [_distance(rgb_color, rgb.int2rgb(dxf_color))
                 for dxf_color in rgb.dxf_default_colors]
    min_dist = min(distances)
    idx_min = distances.index(min_dist)
    if idx_min == 0:
        idx_min = BLACK
    elif idx_min == 7:
        idx_min = WHITE
    return idx_min
