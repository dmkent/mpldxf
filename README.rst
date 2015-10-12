+++++++++++++++++++++++++++++++
Matplotlib backend for dxf
+++++++++++++++++++++++++++++++

Overview
+++++++++++++++++++++++++++++++

This is a matplotlib backend that enables matplotlib to save figures as 
DXF drawings. DXF is a drawing format that is used by computer aided
design (CAD) tools.

This package builds on the ezdxf package by Manfred Moitzi:

     http://bitbucket.org/mozman/ezdxf

Usage
+++++++++++++++++++++++++++++++

First you need to register the backend with matplotlib::

  import matplotlib
  from mpldxf import FigureCanvasDxf
  matplotlib.backend_bases.register_backend('dxf', FigureCanvasDxf)

You can then save your figure::

  from matplotlib import pyplot as plt
  plt.plot(range(10))
  plt.savefig('myplot.dxf')

Warning
++++++++++++++++++++

This is very much a work in progress. Not all matplotlib plot types will
render correctly. Text alignment and sizing in particular need work.
