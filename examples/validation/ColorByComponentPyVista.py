from trame.app import get_server
from trame.widgets import vuetify, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

import pyvista as pv
from trame_vtk.modules.vtk.serializers import encode_lut

pv.OFF_SCREEN = True

# Can only be set once before initialization
encode_lut(True)  # true: ok / false: ko

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# VTK code
# -----------------------------------------------------------------------------

plotter = pv.Plotter()
actor = plotter.add_mesh(
    pv.Sphere(phi_resolution=60, theta_resolution=60),
)

mapper = actor.mapper
mapper.SelectColorArray("Normals")
mapper.SetScalarModeToUsePointFieldData()
mapper.SetScalarVisibility(True)
mapper.SetUseLookupTableScalarRange(True)

lut = mapper.lookup_table
lut.cmap = "viridis"
lut.scalar_range = (-1, 1)
lut.SetVectorModeToComponent()
lut.SetVectorSize(3)

plotter.render()
plotter.reset_camera()


@state.change("component_idx")
def color_by_array(component_idx, **kwargs):
    lut.SetVectorModeToComponent()
    lut.SetVectorSize(3)
    lut.SetVectorComponent(component_idx)

    ctrl.remote_view_update()
    ctrl.local_view_update()


@state.change("cmap")
def color_preset(cmap, **kwargs):
    lut.cmap = cmap
    ctrl.remote_view_update()
    ctrl.local_view_update()


with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text("Color By Normal")

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            v_model=("component_idx", 0),
            items=(
                "components",
                [
                    dict(value=0, text="X"),
                    dict(value=1, text="Y"),
                    dict(value=2, text="Z"),
                ],
            ),
            dense=True,
            hide_details=True,
        )
        vuetify.VSelect(
            v_model=("cmap", "viridis"),
            items=(
                "presets",
                [
                    "viridis",
                    "hot",
                ],
            ),
            dense=True,
            hide_details=True,
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VCol(classes="pa-0 fill-height"):
                view = vtk_widgets.VtkLocalView(plotter.render_window, ref="local")
                ctrl.local_view_update = view.update
                ctrl.view_reset_camera.add(view.reset_camera)
                ctrl.view_push_camera.add(view.push_camera)
            with vuetify.VCol(classes="pa-0 fill-height"):
                view = vtk_widgets.VtkRemoteView(plotter.render_window, ref="remote")
                ctrl.remote_view_update = view.update
                ctrl.view_reset_camera.add(view.reset_camera)

server.start()
