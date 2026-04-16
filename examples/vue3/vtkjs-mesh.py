from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from vtkmodules.vtkImagingCore import vtkRTAnalyticSource

from trame.widgets import vtk as vtk_widgets
from trame.widgets import vuetify3

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue3"
state, ctrl = server.state, server.controller

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera

    with layout.content:
        with vuetify3.VContainer(fluid=True, classes="pa-0 fill-height"):
            with vtk_widgets.VtkView() as view:
                ctrl.view_reset_camera = view.reset_camera
                with vtk_widgets.VtkGeometryRepresentation(
                    color_data_range=("[20, 280]",),
                ):
                    vtk_widgets.VtkMesh(
                        "wavelet",
                        dataset=vtkRTAnalyticSource(),
                        field_to_keep="RTData",
                    )


server.start()
