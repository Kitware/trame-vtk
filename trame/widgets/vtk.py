from trame_vtk.widgets.vtk import *


def initialize(server):
    from trame_vtk.modules import common, vtk

    server.enable_module(common)
    server.enable_module(vtk)
