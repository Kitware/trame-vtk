import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from vtkmodules.vtkFiltersSources import vtkConeSource

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa: F401
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from trame.widgets import vtk as vtk_widgets
from trame.widgets import vuetify3

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue3"
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


@state.change("resolution")
def update_cone(resolution=DEFAULT_RESOLUTION, **_):
    cone_source.SetResolution(resolution)
    ctrl.view_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text("Cone Application")

    with layout.toolbar:
        vuetify3.VSpacer()
        vuetify3.VSlider(
            density="compact",
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )
        vuetify3.VDivider(vertical=True, classes="mx-2")
        with vuetify3.VBtn(icon=True, click=update_reset_resolution):
            vuetify3.VIcon("mdi-undo-variant")

    with (
        layout.content,
        vuetify3.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ),
    ):
        view = vtk_widgets.VtkLocalView(renderWindow)
        ctrl.view_update = view.update
        ctrl.view_reset_camera = view.reset_camera

server.start()
