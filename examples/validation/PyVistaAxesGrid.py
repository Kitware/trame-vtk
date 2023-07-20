"""Validate vtkCubeAxesActor serializer.

Make sure that the grid lines color from `vtkCubeAxesActor.GetXAxesLinesProperty.GetColor`
is synchroniezed in addition to text colors.
"""

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify
from trame.widgets.vtk import VtkLocalView

import pyvista as pv

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "PyVista Local View Grid Lines"

# -----------------------------------------------------------------------------
pv.set_plot_theme("document")  # sets black as default for grid lines and text


mesh = pv.Cone()

plotter = pv.Plotter(off_screen=True)
actor = plotter.add_mesh(mesh)
plotter.set_background("lightgrey")  # To see problematic white default set by VTK.js
plotter.show_grid()
plotter.reset_camera(render=False)  # <<< Needed to have a valid initial camera

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
