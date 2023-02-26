from trame.app import get_server
from trame.widgets import vuetify3, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue3"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Client rendering"

DEFAULT_RESOLUTION = 6


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera

    with layout.toolbar:
        vuetify3.VSpacer()
        vuetify3.VSlider(
            density="compact",
            thumb_size=15,
            track_size=2,
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            style="max-width: 300px",
        )
        vuetify3.VDivider(vertical=True, classes="mx-2")
        with vuetify3.VBtn(icon=True, click=update_reset_resolution):
            vuetify3.VIcon("mdi-undo-variant")

    with layout.content:
        with vuetify3.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vtk_widgets.VtkView() as view:
                ctrl.view_update = view.update
                ctrl.view_reset_camera = view.reset_camera
                with vtk_widgets.VtkGeometryRepresentation():
                    vtk_widgets.VtkAlgorithm(
                        vtk_class="vtkConeSource",
                        state=("{ resolution }",),
                    )
                with vtk_widgets.VtkGeometryRepresentation():
                    with vtk_widgets.VtkAlgorithm(
                        vtk_class="vtkTubeFilter",
                        state=(
                            "{ radius: 0.005 * resolution, numberOfSides: 24, capping: resolution < 10 }",
                        ),
                    ):
                        vtk_widgets.VtkPolyData(
                            name="line",
                            points=("[-1, 0, 0, 1, 0, 0]",),
                            lines=("[2, 0, 1]",),
                        )
                with vtk_widgets.VtkGlyphRepresentation(
                    mapper=("{ scaleFactor: 0.0025 }",),
                ):
                    vtk_widgets.VtkAlgorithm(
                        port=0,
                        vtk_class="vtkPlaneSource",
                        state=("{ XResolution: resolution, YResolution: resolution }",),
                    )
                    vtk_widgets.VtkReader(
                        port=1,
                        vtk_class="vtkOBJReader",
                        url="https://raw.githubusercontent.com/plotly/dash-vtk/master/demos/data/cow-nonormals.obj",
                    )


server.start()
