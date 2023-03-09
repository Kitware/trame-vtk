from trame.app import get_server
from trame.widgets import vuetify, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

from vtkmodules.vtkFiltersSources import vtkSphereSource
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
server.client_type = "vue2"
state, ctrl = server.state, server.controller

# -----------------------------------------------------------------------------
# VTK code
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.OffScreenRenderingOn()  # Prevent popup window

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

source = vtkSphereSource()
source.SetPhiResolution(60)
source.SetThetaResolution(60)
mapper = vtkPolyDataMapper()
actor = vtkActor()
mapper.SetInputConnection(source.GetOutputPort())
actor.SetMapper(mapper)
renderer.AddActor(actor)
renderer.ResetCamera()
renderWindow.Render()

mapper.SelectColorArray("Normals")
mapper.SetScalarModeToUsePointFieldData()
mapper.SetScalarVisibility(True)
mapper.SetUseLookupTableScalarRange(True)

lut = mapper.GetLookupTable()
lut.SetRange(-1, 1)
lut.SetHueRange(0.6, 0)
lut.SetVectorModeToComponent()
lut.SetVectorSize(3)


@state.change("component_idx")
def color_by_array(component_idx, **kwargs):
    lut.SetVectorComponent(component_idx)
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

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VCol(classes="pa-0 fill-height"):
                view = vtk_widgets.VtkLocalView(renderWindow, ref="local")
                ctrl.local_view_update = view.update
                ctrl.view_reset_camera.add(view.reset_camera)
            with vuetify.VCol(classes="pa-0 fill-height"):
                view = vtk_widgets.VtkRemoteView(renderWindow, ref="remote")
                ctrl.remote_view_update = view.update
                ctrl.view_reset_camera.add(view.reset_camera)

server.start()
