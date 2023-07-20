from trame.app import get_server
from trame.widgets import vuetify, html, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# for remote view
import vtkmodules.vtkRenderingOpenGL2  # noqa

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

TITLE = "Remote/Local camera sync"

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = TITLE

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

DEFAULT_RESOLUTION = 6


renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

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

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@state.change("resolution")
def update_resolution(resolution, **kwargs):
    cone_source.SetResolution(resolution)
    ctrl.view_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


def push_camera():
    print("Push camera")
    ctrl.view_push_camera()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(TITLE)

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VBtn("Push camera", click=push_camera)
        vuetify.VBtn("Reset resolution", click=update_reset_resolution)
        vuetify.VSlider(
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
            style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr;",
        ):
            with html.Div(
                style="height: 100%;justify-self: stretch;",
            ):
                remote_view = vtk_widgets.VtkRemoteView(
                    renderWindow,
                    ref="view_remote",
                )
                ctrl.view_update.add(remote_view.update)
                ctrl.view_reset_camera.add(remote_view.reset_camera)

            with html.Div(
                style="height: 100%;justify-self: stretch;",
            ):
                local_view = vtk_widgets.VtkLocalView(
                    renderWindow,
                    ref="view_local",
                )
                ctrl.view_update.add(local_view.update)
                ctrl.view_reset_camera.add(local_view.reset_camera)
                ctrl.view_push_camera = local_view.push_camera


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
