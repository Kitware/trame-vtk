#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "trame>=3.13",
#     "trame-vtk>=2.11.14",
#     "trame-vtklocal>=1",
#     "trame-vuetify",
#     "vtk==9.6.20260517.dev0",
# ]
#
# [[tool.uv.index]]
# url = "https://wheels.vtk.org"
# ///

# ---------------------------------------------------------
# Read for context
# https://github.com/Kitware/trame/issues/900
# ---------------------------------------------------------
# Required for rendering initialization
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from trame.app import TrameApp
from trame.ui.vuetify3 import VAppLayout
from vtkmodules import vtkCommonCore
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy
from vtkmodules.vtkFiltersSources import vtkCubeSource

# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from trame.widgets import vtk, vtklocal

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------


def make_pipeline(array, numpy_roundtrip=False):
    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    source = vtkCubeSource()
    source.Update()
    cube = source.GetOutput()

    array_type = getattr(vtkCommonCore, array)
    cell_scalars = array_type()
    cell_scalars.SetName("data")

    for i in range(cube.GetNumberOfCells()):
        cell_scalars.InsertNextValue(i)

    print("Numpy start type", vtk_to_numpy(cell_scalars).dtype)

    if numpy_roundtrip:
        values = vtk_to_numpy(cell_scalars)
        cell_scalars = numpy_to_vtk(values)
        cell_scalars.SetName("data")

    print("Numpy end type", vtk_to_numpy(cell_scalars).dtype)

    cube.GetCellData().SetScalars(cell_scalars)

    mapper = vtkPolyDataMapper()
    mapper.SetInputData(cube)
    mapper.SetScalarModeToUseCellData()
    mapper.SetScalarRange(cell_scalars.GetRange())

    actor = vtkActor()
    actor.SetMapper(mapper)

    renderer.AddActor(actor)
    renderer.SetBackground(0.5, 0.5, 0.5)

    camera = renderer.GetActiveCamera()
    camera.SetPosition(-1, -1, 1)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)

    renderer.ResetCamera()
    renderer.ResetCameraClippingRange()

    return renderWindow


# -----------------------------------------------------------------------------
# Trame
# -----------------------------------------------------------------------------


class App(TrameApp):
    def __init__(self, server=None):
        super().__init__(server)

        self.server.cli.add_argument(
            "array",
            help="VTK array class vtkTypeInt64Array, vtkLongArray, etc.",
        )
        self.server.cli.add_argument(
            "--numpy-roundtrip",
            action="store_true",
            help="Convert array through vtk_to_numpy/numpy_to_vtk before assigning",
        )
        self.server.cli.add_argument(
            "--wasm",
            action="store_true",
            help="Use wasm local rendering",
        )
        args, _ = self.server.cli.parse_known_args()

        self.renderWindow = make_pipeline(
            args.array,
            numpy_roundtrip=args.numpy_roundtrip,
        )

        self._build_ui(args.wasm)

    def _build_ui(self, use_wasm):
        with VAppLayout(self.server) as self.ui:
            if use_wasm:
                vtklocal.LocalView(self.renderWindow)
            else:
                vtk.VtkLocalView(self.renderWindow)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main():
    app = App()
    app.server.start()


if __name__ == "__main__":
    main()
