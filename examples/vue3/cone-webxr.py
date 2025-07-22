from trame.app import get_server
from trame.widgets import vuetify3, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue3"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Local rendering"
state.xr_active = False

DEFAULT_RESOLUTION = 6

# -----------------------------------------------------------------------------
# VTK code
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderer.SetBackground(0.0231, 0.4194, 0.5592)
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.OffScreenRenderingOn()  # Prevent popup window

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtkConeSource()
mapper = vtkPolyDataMapper()
actor = vtkActor()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor.SetMapper(mapper)
renderer.AddActor(actor)
renderer.ResetCamera()
renderWindow.Render()


@state.change("resolution")
def update_cone(resolution=DEFAULT_RESOLUTION, **kwargs):
    cone_source.SetResolution(resolution)
    ctrl.view_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


def toggle_xr():
    if state.xr_active:
        ctrl.stop_xr()
    else:
        ctrl.start_xr(vtk_widgets.VtkWebXRHelper.XrSessionTypes.HmdVR)


with SinglePageLayout(server) as layout:
    layout.title.set_text("WebXR Cone")

    with layout.toolbar:
        vuetify3.VSpacer()
        vuetify3.VSlider(
            density="compact",
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )
        vuetify3.VDivider(vertical=True, classes="mx-2")
        with vuetify3.VBtn(icon=True, click=toggle_xr):
            vuetify3.VIcon("mdi-virtual-reality")

    with layout.content:
        with vuetify3.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vtk_widgets.VtkLocalView(renderWindow) as view:
                ctrl.view_update = view.update

                def on_enter_xr():
                    state.xr_active = True

                def on_exit_xr():
                    state.xr_active = False

                webxr_helper = vtk_widgets.VtkWebXRHelper(
                    draw_controllers_ray=True, enter_xr=on_enter_xr, exit_xr=on_exit_xr
                )
                ctrl.start_xr = webxr_helper.start_xr
                ctrl.stop_xr = webxr_helper.stop_xr

server.start()
