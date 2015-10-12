"""
DXF colour table tools.

Copyright (C) 2014 David M Kent

Distribution of this software without written permission of the
copyright holder is prohibited.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
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
