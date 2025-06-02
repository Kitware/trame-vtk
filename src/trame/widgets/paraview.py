from trame_vtk.widgets.vtk import *  # noqa: F403


def initialize(server):
    from trame_vtk.modules import common, paraview

    server.enable_module(common)
    server.enable_module(paraview)
