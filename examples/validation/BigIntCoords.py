from pathlib import Path

import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from trame.app import get_server
from trame.ui.html import DivLayout
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkIOXML import vtkXMLRectilinearGridReader
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from trame.widgets import vtk

DATA_FILE = (Path(__file__).parent.with_name("data") / "big-int-coord.vtr").resolve()

reader = vtkXMLRectilinearGridReader()
reader.SetFileName(str(DATA_FILE))

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()


mapper = vtkDataSetMapper()
mapper.SetInputConnection(reader.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)

renderer.AddActor(actor)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame viewer
# -----------------------------------------------------------------------------

server = get_server(client_type="vue3")
ctrl = server.controller
with DivLayout(server) as layout:
    layout.root.style = "width: calc(100vw - 16px); height: calc(100vh - 16px);"
    ctrl.reset_camera = vtk.VtkLocalView(
        renderWindow,
        on_ready=ctrl.reset_camera,
    ).reset_camera

server.start()
