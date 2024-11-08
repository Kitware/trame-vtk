import asyncio

from trame.app import get_server, asynchronous
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as v3, vtk as vtk_widgets

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtkConeSource()
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)
renderer.AddActor(actor)
renderer.ResetCamera()

server = get_server(client_type="vue3")
state, ctrl = server.state, server.controller


async def animate():
    while True:
        await asyncio.sleep(1.0 / state.anime_rate)
        if state.mode == "animate":
            renderer.GetActiveCamera().Azimuth(1)
            renderWindow.Modified()
        if state.mode == "update":
            renderer.GetActiveCamera().Azimuth(1)
            ctrl.view_update()


@state.change("mode")
def on_animation_change(mode, **_):
    if mode == "animate":
        ctrl.view_start_animation(state.fps, 60, 1)
    else:
        ctrl.view_stop_animation()


asynchronous.create_task(animate())

with SinglePageLayout(server) as layout:
    layout.title.set_text("Anim({{ anime_rate }}) Push Rate {{ fps }}")

    with layout.toolbar:
        v3.VSelect(
            v_model=("mode", "stop"),
            items=("modes", ["stop", "animate", "update"]),
            hide_details=True,
        )
        v3.VSlider(
            v_model=("fps", 30),
            min=10,
            max=120,
            step=5,
            hide_details=True,
            classes="mx-4",
            style="max-width: 200px;",
        )
        v3.VSlider(
            v_model=("anime_rate", 30),
            min=10,
            max=120,
            step=5,
            hide_details=True,
            classes="mx-4",
            style="max-width: 200px;",
        )

    with layout.content:
        with v3.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            view = vtk_widgets.VtkRemoteView(
                renderWindow, interactive_quality=80, interactive_ratio=1
            )
            ctrl.view_update = view.update
            ctrl.view_start_animation = view.start_animation
            ctrl.view_stop_animation = view.stop_animation

if __name__ == "__main__":
    server.start()
