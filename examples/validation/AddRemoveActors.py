from trame.app import get_server
from trame.widgets import vuetify, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# -----------------------------------------------------------------------------
# Trame initialization
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

state.trame__title = "VTK Remote View - Local Rendering"

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


def create_pipeline(source):
    mapper = vtkPolyDataMapper()
    actor = vtkActor()
    if hasattr(source, "GetOutputPort"):
        mapper.SetInputConnection(source.GetOutputPort())
    else:
        mapper.SetInputData(source)
    actor.SetMapper(mapper)
    return actor


cone_source = vtkConeSource()
cone_actor = create_pipeline(cone_source)
renderer.AddActor(cone_actor)

sphere_source = vtkSphereSource()
sphere_actor = create_pipeline(sphere_source)
renderer.AddActor(sphere_actor)

# Dummy actor
filter = vtkOutlineFilter()
filter.SetInputConnection(cone_source.GetOutputPort())
renderer.AddActor(create_pipeline(filter))

renderer.ResetCamera()
renderWindow.Render()


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@state.change("resolution")
def update_cone(resolution=DEFAULT_RESOLUTION, **kwargs):
    cone_source.SetResolution(resolution)
    ctrl.view_update()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


@state.change("show_cone")
def update_cone(show_cone, **kwargs):
    if show_cone:
        renderer.AddActor(cone_actor)
    else:
        renderer.RemoveActor(cone_actor)
    ctrl.view_update()


@state.change("show_sphere")
def update_cone(show_sphere, **kwargs):
    if show_sphere:
        renderer.AddActor(sphere_actor)
    else:
        renderer.RemoveActor(sphere_actor)
    ctrl.view_update()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text("Cone Application")

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSlider(
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )
        vuetify.VDivider(vertical=True, classes="mx-2")
        with vuetify.VBtn(icon=True, click=update_reset_resolution):
            vuetify.VIcon("mdi-undo-variant")

        vuetify.VCheckbox(
            v_model=("show_cone", True), label="Cone", dense=True, hide_details=True
        )
        vuetify.VCheckbox(
            v_model=("show_sphere", True), label="Sphere", dense=True, hide_details=True
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk_widgets.VtkLocalView(renderWindow, ref="view")
            ctrl.view_update = view.update
            ctrl.view_reset_camera = view.reset_camera


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
