from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtkConeSource()
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)
axes = vtkAxesActor()
# axes.SetShaftTypeToCylinder()
axes.SetShaftTypeToLine()
transform = vtkTransform()
transform.Translate(1.0, 0.0, 0.0)
axes.SetUserTransform(transform)
renderer.AddActor(axes)

renderer.AddActor(actor)
renderer.ResetCamera()

server = get_server()
server.client_type = "vue2"
ctrl = server.controller

with SinglePageLayout(server) as layout:
    layout.title.set_text("Hello trame")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VCol(classes="pa-0 ma-1 fill-height"):
                vtk_widgets.VtkLocalView(renderWindow)
            with vuetify.VCol(classes="pa-0 ma-1 fill-height"):
                vtk_widgets.VtkRemoteView(renderWindow, interactive_ratio=1)


if __name__ == "__main__":
    server.start()
