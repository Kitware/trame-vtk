"""Validate Int64 usage with VTK.js."""

import numpy as np
import pyvista as pv
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout

# Just for using this script in testing
from trame_client.utils.testing import enable_testing

from trame.widgets import html, vuetify
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

server = enable_testing(get_server(), "local_rendering_ready")
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "Int64 Validation"
state.local_rendering_ready = 0

# -----------------------------------------------------------------------------

mesh = pv.Sphere()
mesh["data"] = np.arange(mesh.n_cells, dtype=np.int64)

plotter = pv.Plotter(off_screen=True)
actor = plotter.add_mesh(mesh, scalars="data")
plotter.reset_camera()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(state.trame__title)

    with layout.toolbar:
        vuetify.VSpacer()
        html.Div("{{ local_rendering_ready }}", classes="readyCount")

    with (
        layout.content,
        vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ),
    ):
        with vuetify.VCol(classes="fill-height"):
            view = VtkLocalView(
                plotter.ren_win,
                on_ready="local_rendering_ready++",
            )
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera
        with vuetify.VCol(classes="fill-height"):
            VtkRemoteView(plotter.ren_win)

    # hide footer
    layout.footer.hide()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
