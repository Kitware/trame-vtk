from trame.app import get_server
from trame.widgets import html, vuetify3, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout

from vtkmodules.vtkFiltersSources import vtkConeSource
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
server.client_type = "vue3"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Remote rendering"

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


@state.change("resolution")
def update_cone(resolution=DEFAULT_RESOLUTION, **kwargs):
    cone_source.SetResolution(resolution)
    ctrl.view_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text("Cone Application")

    with layout.toolbar:
        html.Div("{{ mode }}")
        vuetify3.VSpacer()
        vuetify3.VCheckbox(
            density="compact",
            v_model=("mode", "remote"),
            false_icon="mdi-image",
            true_icon="mdi-rotate-3d",
            true_value="local",
            false_value="remote",
            hide_details=True,
        )
        vuetify3.VSlider(
            density="compact",
            thumb_size=15,
            track_size=2,
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            style="max-width: 300px",
        )
        vuetify3.VDivider(vertical=True, classes="mx-2")
        with vuetify3.VBtn(icon=True, click=update_reset_resolution):
            vuetify3.VIcon("mdi-undo-variant")

    with layout.content:
        with vuetify3.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk_widgets.VtkRemoteLocalView(renderWindow, mode=("mode",))
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera
            view.push_remote_camera_on_end_interaction()

server.start()
