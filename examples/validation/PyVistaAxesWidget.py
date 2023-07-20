"""Validate axes actor serialization."""

import pyvista as pv
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "Axes Widget Validation"

# -----------------------------------------------------------------------------

mesh = pv.Cone()

plotter = pv.Plotter(off_screen=True)
actor = plotter.add_mesh(mesh)
plotter.reset_camera()

plotter.add_axes()
axes_widget = plotter.renderer.axes_widget


@state.change("show_widget")
def toggle_axes_widget(show_widget, **kwargs):
    if show_widget:
        plotter.renderer.show_axes()
    else:
        plotter.renderer.hide_axes()
    ctrl.view_update()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(state.trame__title)

    with layout.toolbar:
        vuetify.VSpacer()

        vuetify.VCheckbox(
            v_model=("show_widget", True),
            on_icon="mdi-axis-arrow-info",
            off_icon="mdi-axis-arrow-info",
            dense=True,
            hide_details=True,
            classes="my-0 py-0 ml-1",
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VCol(classes="fill-height"):
                view = VtkLocalView(
                    plotter.ren_win, ref="local"
                )  # or widgets=[axes_widget]
                ctrl.view_update.add(view.update)
                ctrl.view_reset_camera.add(view.reset_camera)
                ctrl.view_widgets_set = view.set_widgets
                view.set_widgets([axes_widget])  # or at constructor

            with vuetify.VCol(classes="fill-height"):
                view = VtkRemoteView(plotter.ren_win, ref="remote")
                ctrl.view_update.add(view.update)
                ctrl.view_reset_camera.add(view.reset_camera)

    # hide footer
    layout.footer.hide()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
