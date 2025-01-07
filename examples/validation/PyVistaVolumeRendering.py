"""Validate volume rendering with VTK.js."""

import os
import sys
import pyvista as pv
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

# Just for using this script in testing
from trame_client.utils.testing import enable_testing

if os.environ.get("PYTEST_CURRENT_TEST") or "--test" in sys.argv:
    server = enable_testing(get_server(), "local_rendering_ready")
else:
    server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "Volume Validation"
state.local_rendering_ready = 0

# -----------------------------------------------------------------------------

image = pv.Wavelet()

plotter = pv.Plotter(off_screen=True)
actor = plotter.add_volume(image)
plotter.reset_camera()


def update_local_rendering():
    ctrl.view_update()
    ctrl.view_reset_camera()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(state.trame__title)

    with layout.toolbar:
        vuetify.VSpacer()
        html.Div("{{ local_rendering_ready }}", classes="readyCount")
        vuetify.VBtn("Update", click=update_local_rendering)

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VCol(classes="fill-height"):
                view = VtkLocalView(
                    plotter.ren_win,
                    ref="local",
                    on_ready="local_rendering_ready++",
                )
                ctrl.view_update = view.update
                ctrl.view_reset_camera = view.reset_camera
            with vuetify.VCol(classes="fill-height"):
                VtkRemoteView(
                    plotter.ren_win,
                    ref="remote",
                )

    # hide footer
    layout.footer.hide()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
