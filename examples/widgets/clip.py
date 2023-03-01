from trame.app import get_server
from trame.widgets import vuetify, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

# VTK factory initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

from vtkmodules.vtkFiltersGeneral import vtkClipDataSet
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
from vtkmodules.vtkCommonDataModel import vtkPlane
from vtkmodules.vtkInteractionWidgets import vtkImplicitPlaneWidget2
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
)


from trame_vtk.modules.vtk.widget import WidgetManager

# -----------------------------------------------------------------------------
# VTK
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.OffScreenRenderingOn()  # Prevent popup window

render_window_interactor = vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)
render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

source = vtkRTAnalyticSource()

clip_plane = vtkPlane()
clip = vtkClipDataSet()
clip.SetInputConnection(source.GetOutputPort())
clip.SetClipFunction(clip_plane)
clip.SetInsideOut(True)

outline = vtkOutlineFilter()
outline.SetInputConnection(source.GetOutputPort())

clip_mapper = vtkDataSetMapper()
clip_mapper.SetInputConnection(clip.GetOutputPort())
clip_actor = vtkActor()
clip_actor.SetMapper(clip_mapper)
renderer.AddActor(clip_actor)

outline_mapper = vtkDataSetMapper()
outline_mapper.SetInputConnection(outline.GetOutputPort())
outline_actor = vtkActor()
outline_actor.SetMapper(outline_mapper)
renderer.AddActor(outline_actor)

renderer.ResetCamera()

# Data info extract
source.Update()
source_ds = source.GetOutput()
source_bounds = source_ds.GetBounds()
source_data_range = source_ds.GetPointData().GetScalars().GetRange()

# Color handling
clip_mapper.SetScalarModeToUsePointFieldData()
clip_mapper.SelectColorArray("RTData")
clip_mapper.SetScalarRange(source_data_range)


# Setup widget
widget_manager = WidgetManager(renderer)
plane_widget = widget_manager.add_widget(vtkImplicitPlaneWidget2)


def on_widget_interaction(*args):
    if state.live_update:
        plane_widget.GetPlane(clip_plane)


def on_widget_done(*args):
    plane_widget.GetPlane(clip_plane)


plane_widget.SetPlaceFactor(1)
plane_widget.PlaceWidget(source_bounds)
plane_widget.on_interaction(on_widget_interaction)
plane_widget.on_end_interaction(on_widget_done)
on_widget_done()  # for initial sync


# -----------------------------------------------------------------------------
# Trame
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller


@state.change("show_widget")
def on_widget_show(show_widget, **kwargs):
    if show_widget:
        plane_widget.enable()
    else:
        plane_widget.disable()
    ctrl.view_update()


with SinglePageLayout(server) as layout:
    layout.title.set_text("Clip with plane widget")

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VCheckbox(
            v_model=("show_widget", False),
            dense=True,
            hide_details=True,
            off_icon="mdi-paper-cut-vertical",
            on_icon="mdi-paper-cut-vertical",
            classes="mt-0",
        )
        vuetify.VCheckbox(
            v_model=("live_update", False),
            dense=True,
            hide_details=True,
            off_icon="mdi-link-off",
            on_icon="mdi-link",
            classes="mt-0",
        )
        with vuetify.VBtn(icon=True, click=ctrl.view_reset_camera):
            vuetify.VIcon("mdi-crop-free")

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            view = vtk_widgets.VtkRemoteView(
                render_window,
                interactive_ratio=1,
            )
            ctrl.view_reset_camera = view.reset_camera
            ctrl.view_update = view.update


if __name__ == "__main__":
    server.start()
