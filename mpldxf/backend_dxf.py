"""
A backend to export DXF using a custom DXF renderer.

This allows saving of DXF figures.

Use as a matplotlib external backend:

  import matplotlib
  matplotlib.use('module://mpldxf.backend_dxf')

or register:

  matplotlib.backend_bases.register_backend('dxf', FigureCanvasDxf)

Based on matplotlib.backends.backend_template.py.

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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import sys
import math

import matplotlib
from matplotlib.backend_bases import (RendererBase, FigureCanvasBase,
                                      GraphicsContextBase, FigureManagerBase)
from matplotlib.transforms import Affine2D
import matplotlib.transforms as transforms
import matplotlib.collections as mplc
import numpy as np
from shapely.geometry import LineString, Polygon
import ezdxf

from . import dxf_colors

# When packaged with py2exe ezdxf has issues finding its templates
# We tell it where to find them using this.
# Note we also need to make sure they get packaged by adding them to the
# configuration in setup.py
if hasattr(sys, 'frozen'):
    ezdxf.options.template_dir = os.path.dirname(sys.executable)


def rgb_to_dxf(rgb_val):
    """Convert an RGB[A] colour to DXF colour index.

       ``rgb_val`` should be a tuple of values in range 0.0 - 1.0. Any
       alpha value is ignored.
    """
    if rgb_val is None:
        dxfcolor = dxf_colors.WHITE
    # change black to white
    elif np.allclose(np.array(rgb_val[:3]), np.zeros(3)):
        dxfcolor = dxf_colors.nearest_index([255,255,255])
    else:
        dxfcolor = dxf_colors.nearest_index([255.0 * val for val in rgb_val[:3]])
    return dxfcolor


class RendererDxf(RendererBase):
    """
    The renderer handles drawing/rendering operations.

    Renders the drawing using the ``ezdxf`` package.
    """
    def __init__(self, width, height, dpi, dxfversion):
        RendererBase.__init__(self)
        self.height = height
        self.width = width
        self.dpi = dpi
        self.dxfversion = dxfversion
        self._init_drawing()
        self._groupd = []

    def _init_drawing(self):
        """Create a drawing, set some global information and add
           the layers we need.
        """
        drawing = ezdxf.new(dxfversion=self.dxfversion)
        modelspace = drawing.modelspace()
        drawing.header['$EXTMIN'] = (0, 0, 0)
        drawing.header['$EXTMAX'] = (self.width, self.height, 0)
        self.drawing = drawing
        self.modelspace = modelspace

    def clear(self):
        """Reset the renderer."""
        super(RendererDxf, self).clear()
        self._init_drawing()

    def _get_polyline_attribs(self, gc):
        attribs = {}
        attribs['color'] = rgb_to_dxf(gc.get_rgb())
        return attribs

    def _clip_mpl(self, gc, vertices, obj):
        # clip the polygon if clip rectangle present
        bbox = gc.get_clip_rectangle()
        if bbox is not None:
            cliprect = [[bbox.x0, bbox.y0],
                        [bbox.x1, bbox.y0],
                        [bbox.x1, bbox.y1],
                        [bbox.x0, bbox.y1]]

            if obj == 'patch':
                vertices = ezdxf.math.clip_polygon_2d(cliprect, vertices)
            elif obj == 'line2d':
                cliprect = Polygon(cliprect)
                line = LineString(vertices)
                vertices = line.intersection(cliprect).coords

        return vertices

    def _draw_mpl_lwpoly(self, gc, path, transform, obj):
        #TODO rework for BEZIER curves
        if obj=='patch':
            close = True
        elif obj=='line2d':
            close = False

        dxfattribs = self._get_polyline_attribs(gc)
        vertices = path.transformed(transform).vertices

        # clip the polygon if clip rectangle present
        vertices = self._clip_mpl(gc, vertices, obj=obj)

        entity = self.modelspace.add_lwpolyline(points=vertices,
                                        close=close,
                                        dxfattribs=dxfattribs)
        return entity

    def _draw_mpl_line2d(self, gc, path, transform):
        line = self._draw_mpl_lwpoly(gc, path, transform, obj='line2d')

    def _draw_mpl_patch(self, gc, path, transform, rgbFace=None): 
        '''Draw a matplotlib patch object
        '''

        poly = self._draw_mpl_lwpoly(gc, path, transform, obj='patch')

        # check to see if the patch is filled
        if rgbFace is not None:
            hatch = self.modelspace.add_hatch(color=rgb_to_dxf(rgbFace))
            hpath = hatch.paths.add_polyline_path(
                # get path vertices from associated LWPOLYLINE entity
                poly.get_points(format="xyb"),
                # get closed state also from associated LWPOLYLINE entity
                is_closed=poly.closed)

            # Set association between boundary path and LWPOLYLINE
            hatch.associate(hpath, [poly])

        self._draw_mpl_hatch(gc, path, transform, pline=poly)

    def _draw_mpl_hatch(self, gc, path, transform, pline):
        '''Draw MPL hatch
        '''

        hatch = gc.get_hatch()
        if hatch is not None:
            # find extents and center of the original unclipped parent path
            ext = path.get_extents(transform=transform)
            dx = ext.x1-ext.x0
            cx = 0.5*(ext.x1+ext.x0)
            dy = ext.y1-ext.y0
            cy = 0.5*(ext.y1+ext.y0)

            # matplotlib uses a 1-inch square hatch, so find out how many rows
            # and columns will be needed to fill the parent path
            rows, cols = math.ceil(dy/self.dpi)-1, math.ceil(dx/self.dpi)-1

            # get color of the hatch
            rgb = gc.get_hatch_color()
            dxfcolor = rgb_to_dxf(rgb)

            # get hatch paths
            hpath = gc.get_hatch_path()

            # this is a tranform that produces a properly scaled hatch in the center
            # of the parent hatch
            _transform = Affine2D().translate(-0.5, -0.5).scale(self.dpi).translate(cx, cy)
            hpatht = hpath.transformed(_transform)

            # print("\tHatch Path:", hpatht)
            # now place the hatch to cover the parent path
            for irow in range(-rows, rows+1):
                for icol in range(-cols, cols+1):
                    # transformation from the center of the parent path
                    _trans = Affine2D().translate(icol*self.dpi, irow*self.dpi)
                    # transformed hatch
                    _hpath = hpatht.transformed(_trans)

                    # turn into list of vertices to make up polygon
                    _path = _hpath.to_polygons(closed_only=False) 

                    for vertices in _path:
                        # clip each set to the parent path
                        if len(vertices) == 2:
                            clippoly = Polygon(pline.vertices())
                            line = LineString(vertices)
                            clipped = line.intersection(clippoly).coords
                        else:
                            clipped = ezdxf.math.clip_polygon_2d(pline.vertices(), vertices)

                        # if there is something to plot
                        if len(clipped)>0:
                            if len(vertices) == 2:
                                attrs = {'color': dxfcolor}
                                self.modelspace.add_lwpolyline(points=clipped,
                                                dxfattribs=attrs)
                            else:
                                # A non-filled polygon or a line - use LWPOLYLINE entity
                                hatch = self.modelspace.add_hatch(color=dxfcolor)
                                line = hatch.paths.add_polyline_path(clipped)

    def draw_path(self, gc, path, transform, rgbFace=None):
        # print('\nEntered ###DRAW_PATH###')
        # print('\t', self._groupd)
        # print('\t', gc.__dict__, rgbFace)
        # print('\t', gc.get_sketch_params())
        # print('\tMain Path', path.__dict__)
        # hatch = gc.get_hatch()
        # if hatch is not None:
        #     print('\tHatch Path', gc.get_hatch_path().__dict__)

        if self._groupd[-1] == 'patch':
            # print('Draw Patch')
            line = self._draw_mpl_patch(gc, path, transform, rgbFace)

        elif self._groupd[-1] == 'line2d':
            line = self._draw_mpl_line2d(gc, path, transform) 


    # Note if this is used then tick marks and lines with markers go through this function
    def draw_markers(self, gc, marker_path, marker_trans, path, trans, rgbFace=None):
        # print('\nEntered ###DRAW_MARKERS###')
        # print('\t', self._groupd)
        # print('\t', gc.__dict__)
        # print('\tMarker Path:', type(marker_path), marker_path.transformed(marker_trans).__dict__)
        # print('\tPath:', type(path), path.transformed(trans).__dict__)
        if (self._groupd[-1] == 'line2d') & ('tick' in self._groupd[-2]):
            newpath = path.transformed(trans)
            dx, dy = newpath.vertices[0]
            _trans = marker_trans + Affine2D().translate(dx, dy)
            line = self._draw_mpl_line2d(gc, marker_path, _trans) 
        # print('\tLeft ###DRAW_MARKERS###')

    def draw_image(self, gc, x, y, im):
        pass

    def draw_text(self, gc, x, y, s, prop, angle, ismath=False, mtext=None):
        # print('\nEntered ###DRAW_TEXT###')
        # print('\t', self._groupd)
        # print('\t', gc.__dict__)

        fontsize = self.points_to_pixels(prop.get_size_in_points())
        dxfcolor = rgb_to_dxf(gc.get_rgb())

        s=s.replace(u"\u2212", "-")
        s.encode('ascii', 'ignore').decode()
        text = self.modelspace.add_text(s, {
            'height': fontsize,
            'rotation': angle,
            'color': dxfcolor,
        })

        halign = self._map_align(mtext.get_ha(), vert=False)
        valign = self._map_align(mtext.get_va(), vert=True)
        align = valign
        if align:
            align += '_'
        align += halign

        # need to get original points for text anchoring
        pos = mtext.get_unitless_position()
        x, y = mtext.get_transform().transform(pos)

        p1 = x, y
        text.set_pos(p1, align=align)
        # print('Left ###TEXT###')

    def _map_align(self, align, vert=False):
        """Translate a matplotlib text alignment to the ezdxf alignment."""
        if align in ['right', 'center', 'left', 'top',
                     'bottom', 'middle']:
            align = align.upper()
        elif align == 'baseline':
            align = ''
        elif align == 'center_baseline':
            align = 'MIDDLE'
        else:
            # print(align)
            raise NotImplementedError
        if vert and align == 'CENTER':
            align = 'MIDDLE'
        return align

    def open_group(self, s, gid=None):
        # docstring inherited
        self._groupd.append(s)

    def close_group(self, s):
        self._groupd.pop(-1)

    def flipy(self):
        return False

    def get_canvas_width_height(self):
        return self.width, self.height

    def new_gc(self):
        return GraphicsContextBase()

    def points_to_pixels(self, points):
        return points / 72.0 * self.dpi


class FigureCanvasDxf(FigureCanvasBase):
    """
    A canvas to use the renderer. This only implements enough of the
    API to allow the export of DXF to file.
    """

    #: The DXF version to use. This can be set to another version
    #: supported by ezdxf if desired.
    DXFVERSION = 'AC1032'

    def get_dxf_renderer(self, cleared=False):
        """Get a renderer to use. Will create a new one if we don't
           alreadty have one or if the figure dimensions or resolution have
           changed.
        """
        l, b, w, h = self.figure.bbox.bounds
        key = w, h, self.figure.dpi
        try:
            self._lastKey, self.dxf_renderer
        except AttributeError:
            need_new_renderer = True
        else:
            need_new_renderer = (self._lastKey != key)

        if need_new_renderer:
            self.dxf_renderer = RendererDxf(w, h, self.figure.dpi,
                                              self.DXFVERSION)
            self._lastKey = key
        elif cleared:
            self.dxf_renderer.clear()
        return self.dxf_renderer

    def draw(self):
        """
        Draw the figure using the renderer
        """
        renderer = self.get_dxf_renderer()
        self.figure.draw(renderer)
        return renderer.drawing

    # Add DXF to the class-scope filetypes dictionary
    filetypes = FigureCanvasBase.filetypes.copy()
    filetypes['dxf'] = 'DXF'

    def print_dxf(self, filename, *args, **kwargs):
        """
        Write out a DXF file.
        """
        drawing = self.draw()
        drawing.saveas(filename)

    def get_default_filetype(self):
        return 'dxf'

FigureManagerDXF = FigureManagerBase

########################################################################
#
# Now just provide the standard names that backend.__init__ is expecting
#
########################################################################

FigureCanvas = FigureCanvasDxf
