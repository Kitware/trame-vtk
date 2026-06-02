from trame_vtk.widgets.vtk import *  # noqa: F403


def initialize(server):
    from trame_vtk.modules import common, vtk  # noqa: PLC0415

    server.enable_module(common)
    server.enable_module(vtk)
