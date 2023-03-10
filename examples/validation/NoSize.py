from trame.app import get_server
from trame.widgets import vuetify, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Local rendering"

DEFAULT_RESOLUTION = 6

# -----------------------------------------------------------------------------
# VTK code
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.OffScreenRenderingOn()  # Prevent popup window

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtkConeSource()
mapper = vtkPolyDataMapper()
actor = vtkActor()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor.SetMapper(mapper)

renderer.AddActor(actor)
renderer.ResetCamera()
renderWindow.Render()


renderer_v2 = vtkRenderer()
renderWindow_v2 = vtkRenderWindow()
renderWindow_v2.AddRenderer(renderer_v2)
renderWindow_v2.OffScreenRenderingOn()  # Prevent popup window

renderWindowInteractor_v2 = vtkRenderWindowInteractor()
renderWindowInteractor_v2.SetRenderWindow(renderWindow_v2)
renderWindowInteractor_v2.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

sphere_source = vtkSphereSource()
mapper_v2 = vtkPolyDataMapper()
actor_v2 = vtkActor()
mapper_v2.SetInputConnection(sphere_source.GetOutputPort())
actor_v2.SetMapper(mapper_v2)

renderer_v2.AddActor(actor_v2)
renderer_v2.ResetCamera()
renderWindow_v2.Render()

with SinglePageLayout(server) as layout:
    layout.title.set_text("No window size")
    layout.icon.click = ctrl.view_reset_camera

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VCheckbox(
            v_model=("show", False),
            off_icon="mdi-eye-off",
            on_icon="mdi-eye",
            classes="my-0",
            dense=True,
            hide_details=True,
        )

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            with vuetify.VCol(classes="pa-0 fill-height"):
                with vtk_widgets.VtkRemoteView(renderWindow, ref="v1") as view:
                    ctrl.view_reset_camera.add(view.reset_camera)
            with vuetify.VCol(classes="pa-0 fill-height", v_show="show"):
                with vtk_widgets.VtkRemoteView(renderWindow_v2, ref="v2") as view:
                    ctrl.view_reset_camera.add(view.reset_camera)

server.start()
