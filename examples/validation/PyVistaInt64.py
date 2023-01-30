"""Validate Int64 usage with VTK.js."""

import pyvista as pv
import numpy as np
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify
from trame.widgets.vtk import VtkLocalView

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "Int64 Validation"

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

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = VtkLocalView(plotter.ren_win)
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera

    # hide footer
    layout.footer.hide()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
