import vtk

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html
from trame.widgets.vtk import VtkLocalView, VtkRemoteView

# Just for using this script in testing
from trame_client.utils.testing import enable_testing

server = enable_testing(get_server(), "local_rendering_ready")
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "VTK Volume Rendering"
state.local_rendering_ready = 0

# MAPPER_TYPE = "FixedPoint"
MAPPER_TYPE = "Smart"
# MAPPER_TYPE = "GPU"
# MAPPER_TYPE = "RayCast"
MAPPERS = {
    "FixedPoint": vtk.vtkFixedPointVolumeRayCastMapper(),
    "Smart": vtk.vtkSmartVolumeMapper(),
    "GPU": vtk.vtkOpenGLGPUVolumeRayCastMapper(),
    "RayCast": vtk.vtkGPUVolumeRayCastMapper(),
}

# -----------------------------------------------------------------------------
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)
iren.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

source = vtk.vtkRTAnalyticSource()
source.Update()
mapper = MAPPERS[MAPPER_TYPE]
mapper.SetInputConnection(source.GetOutputPort())
actor = vtk.vtkVolume()
actor.SetMapper(mapper)
actor.GetProperty().SetScalarOpacityUnitDistance(10)
ren.AddActor(actor)

colorTransferFunction = vtk.vtkColorTransferFunction()
colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(64.0, 1.0, 0.0, 0.0)
colorTransferFunction.AddRGBPoint(128.0, 0.0, 0.0, 1.0)
colorTransferFunction.AddRGBPoint(192.0, 0.0, 1.0, 0.0)
colorTransferFunction.AddRGBPoint(255.0, 0.0, 0.2, 0.0)

opacityTransferFunction = vtk.vtkPiecewiseFunction()
opacityTransferFunction.AddPoint(20, 0.0)
opacityTransferFunction.AddPoint(255, 0.2)

volumeProperty = vtk.vtkVolumeProperty()
volumeProperty.SetColor(colorTransferFunction)
volumeProperty.SetScalarOpacity(opacityTransferFunction)
volumeProperty.ShadeOn()
volumeProperty.SetInterpolationTypeToLinear()

actor.SetProperty(volumeProperty)

cube = vtk.vtkCubeAxesActor()
cube.SetCamera(ren.GetActiveCamera())
cube.SetBounds(source.GetOutput().GetBounds())
ren.AddActor(cube)

iren.Initialize()
ren.ResetCamera()
ren.SetBackground(0.7, 0.7, 0.7)
renWin.Render()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.view_reset_camera
    layout.title.set_text(state.trame__title)

    with layout.toolbar:
        vuetify.VSpacer()
        html.Div("{{ local_rendering_ready }}", classes="readyCount")

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vuetify.VContainer(
                fluid=True, classes="pa-0 fill-height", style="width: 50%;"
            ):
                local = VtkLocalView(renWin, on_ready="local_rendering_ready++")
            with vuetify.VContainer(
                fluid=True, classes="pa-0 fill-height", style="width: 50%;"
            ):
                remote = VtkRemoteView(renWin)

    # hide footer
    layout.footer.hide()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
