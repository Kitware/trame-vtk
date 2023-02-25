import paraview.web.venv  # noqa
from trame.app import get_server
from trame.widgets import html, vuetify, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

from paraview import simple

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Remote rendering"

DEFAULT_RESOLUTION = 6

# -----------------------------------------------------------------------------
# PV code
# -----------------------------------------------------------------------------

cone = simple.Cone()
rep = simple.Show()
view = simple.Render()


@state.change("resolution")
def update_cone(resolution=DEFAULT_RESOLUTION, **kwargs):
    cone.Resolution = resolution
    ctrl.view_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text("Cone Application")

    with layout.toolbar:
        html.Div("{{ mode }}")
        vuetify.VSpacer()
        vuetify.VCheckbox(
            v_model=("mode", "remote"),
            off_icon="mdi-image",
            on_icon="mdi-rotate-3d",
            true_value="local",
            false_value="remote",
            dense=True,
            hide_details=True,
        )
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

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            html_view = vtk_widgets.VtkRemoteLocalView(view, mode=("mode",))
            ctrl.view_update = html_view.update
            ctrl.view_reset_camera = html_view.reset_camera
            html_view.push_remote_camera_on_end_interaction()


server.start()
