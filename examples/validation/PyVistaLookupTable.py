"""Validate vtkLookupTable serializer with N Colors."""

import pyvista as pv
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html, vtk as vtk_widgets

# Just for using this script in testing
from trame_client.utils.testing import enable_testing

server = enable_testing(get_server(), "local_rendering_ready")
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "PyVista Lookup Table N Colors"
state.local_rendering_ready = 0

# -----------------------------------------------------------------------------
pv.set_plot_theme("document")


mesh = pv.Wavelet()

plotter = pv.Plotter(off_screen=True)
actor = plotter.add_mesh(mesh, n_colors=7)
plotter.set_background("lightgrey")
plotter.view_isometric()

# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(state.trame__title)

    with layout.toolbar:
        vuetify.VSpacer()
        html.Div("{{ local_rendering_ready }}", classes="readyCount")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VContainer(
                fluid=True, classes="pa-0 fill-height", style="width: 50%;"
            ):
                local = vtk_widgets.VtkLocalView(
                    plotter.ren_win,
                    on_ready="local_rendering_ready++",
                )
            with vuetify.VContainer(
                fluid=True, classes="pa-0 fill-height", style="width: 50%;"
            ):
                remote = vtk_widgets.VtkRemoteView(
                    plotter.ren_win,
                )

            def view_update(**kwargs):
                local.update(**kwargs)
                remote.update(**kwargs)

            def view_reset_camera(**kwargs):
                local.reset_camera(**kwargs)
                remote.reset_camera(**kwargs)

            ctrl.view_update = view_update
            ctrl.view_reset_camera = view_reset_camera

            ctrl.on_server_ready.add(view_update)

    # hide footer
    layout.footer.hide()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
