from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from vtkmodules.vtkFiltersSources import vtkConeSource

from trame.widgets import vtk as vtk_widgets
from trame.widgets import vuetify

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Client rendering"

DEFAULT_RESOLUTION = 6
cone_generator = vtkConeSource()


@state.change("resolution")
def update_cone(resolution, **_):
    cone_generator.SetResolution(resolution)
    ctrl.mesh_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSlider(
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )
        vuetify.VDivider(vertical=True, classes="mx-2")
        with vuetify.VBtn(icon=True, click=update_reset_resolution):
            vuetify.VIcon("mdi-undo-variant")

    with (
        layout.content,
        vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ),
        vtk_widgets.VtkView() as view,
    ):
        ctrl.view_update = view.update
        ctrl.view_reset_camera = view.reset_camera
        with vtk_widgets.VtkGeometryRepresentation():
            html_polydata = vtk_widgets.VtkPolyData("cone", dataset=cone_generator)
            ctrl.mesh_update = html_polydata.update


server.start()
