"""Validate axes actor serialization."""

import pyvista as pv
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "Axes Widget Validation - Subplots"

# -----------------------------------------------------------------------------

mesh = pv.Cone()

plotter = pv.Plotter(off_screen=True, shape=(1, 2))
plotter.subplot(0, 0)
actor = plotter.add_mesh(pv.Cone())
plotter.reset_camera()
plotter.add_axes()
axes_widget_0 = plotter.renderer.axes_widget

plotter.subplot(0, 1)
actor = plotter.add_mesh(pv.Cylinder())
plotter.reset_camera()

plotter.add_axes()
axes_widget_1 = plotter.renderer.axes_widget


@state.change("show_widget_a")
def toggle_axes_widget_a(show_widget_a, **kwargs):
    plotter.subplot(0, 0)
    if show_widget_a:
        plotter.renderer.show_axes()
    else:
        plotter.renderer.hide_axes()
    ctrl.view_update()


@state.change("show_widget_b")
def toggle_axes_widget_b(show_widget_b, **kwargs):
    plotter.subplot(0, 1)
    if show_widget_b:
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
            v_model=("show_widget_a", True),
            on_icon="mdi-axis-arrow-info",
            off_icon="mdi-axis-arrow-info",
            dense=True,
            hide_details=True,
            classes="my-0 py-0 ml-1",
        )

        vuetify.VCheckbox(
            v_model=("show_widget_b", True),
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
                view = VtkLocalView(plotter.ren_win, ref="local")
                ctrl.view_update.add(view.update)
                ctrl.view_reset_camera.add(view.reset_camera)
                view.set_widgets([axes_widget_0, axes_widget_1])  # or at constructor

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
