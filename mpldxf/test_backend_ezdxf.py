"""Test the dxf matplotlib backend.

Copyright (C) 2014 David M Kent

Distribution of this software without written permission of the
copyright holder is prohibited.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""
import os
import shutil
import tempfile
import unittest

import matplotlib
from matplotlib import pyplot as plt
from numpy.random import random

from mpldxf import backend_dxf


matplotlib.backend_bases.register_backend('dxf',
                                          backend_dxf.FigureCanvas)


class DxfBackendTestCase(unittest.TestCase):
    """Tests for the dxf backend."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        plt.clf()
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_plot(self):
        """Test a simple line-plot command."""
        plt.plot(range(5), [4, 3, 2, 1, 0])
        outfile = os.path.join(self.test_dir, 'test_plot.dxf')
        plt.savefig(outfile)
        self.assertTrue(os.path.isfile(outfile))

    def test_boxplot(self):
        """Test a box-plot."""
        plt.boxplot(random((4, 30)))
        outfile = os.path.join(self.test_dir, 'test_boxplot.dxf')
        plt.savefig(outfile)
        self.assertTrue(os.path.isfile(outfile))

    def test_contour(self):
        """Test some contours."""
        plt.contour(random((30, 30)))
        outfile = os.path.join(self.test_dir, 'test_contour.dxf')
        plt.savefig(outfile)
        self.assertTrue(os.path.isfile(outfile))

    def test_contourf(self):
        """Test some filled contours."""
        plt.contourf(random((30, 30)))
        outfile = os.path.join(self.test_dir, 'test_contourf.dxf')
        plt.savefig(outfile)
        self.assertTrue(os.path.isfile(outfile))
