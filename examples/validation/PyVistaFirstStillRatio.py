import pyvista as pv
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

pv.set_plot_theme("document")
mesh = pv.Wavelet()

plotter = pv.Plotter(off_screen=True)
actor = plotter.add_mesh(mesh)
plotter.set_background("lightgrey")
plotter.show_grid()
plotter.view_isometric()

# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------
state.trame__title = "PyVista Remote View Ratios"

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
            view = vtk_widgets.VtkRemoteView(
                plotter.ren_win,
                interactive_ratio=2,
                still_ratio=2,
            )
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera


if __name__ == "__main__":
    server.start()
