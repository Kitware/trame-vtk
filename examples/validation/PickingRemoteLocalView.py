from trame.app import get_server
from trame.ui.html import DivLayout
from trame.widgets import html, client, vtk as vtk_widgets

from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
)

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa


class PickingExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")

        # VTK
        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)

        renderWindowInteractor = vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)
        renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        cone_source = vtkConeSource()
        cone_mapper = vtkPolyDataMapper()
        cone_actor = vtkActor()
        cone_mapper.SetInputConnection(cone_source.GetOutputPort())
        cone_actor.SetMapper(cone_mapper)
        renderer.AddActor(cone_actor)

        sphere_source = vtkSphereSource()
        sphere_mapper = vtkPolyDataMapper()
        sphere_actor = vtkActor()
        sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())
        sphere_actor.SetMapper(sphere_mapper)
        renderer.AddActor(sphere_actor)

        renderer.ResetCamera()
        renderWindow.Render()

        self.render_window = renderWindow

        # UI
        self.ui = self._build_ui()

    def on_click(self, event):
        print(f"picking-click: {event}")

    def on_select(self, event):
        print("picking-select:", event)

    def on_hover(self, event):
        print(f"picking-hover: {event}")

    def _build_ui(self):
        with DivLayout(self.server) as layout:
            client.Style("html, body { padding: 0; margin: 0; }")
            layout.root.style = "width: 100vw; height: 100vh;"

            with html.Select(
                v_model="viewMode",
                style="position: absolute; z-index: 10; top: 10px; right: 100px;",
            ):
                for name in ["remote", "local"]:
                    html.Option(name, value=name)

            with html.Select(
                v_model="picking_modes",
                multiple=True,
                style="position: absolute; z-index: 10; top: 10px; right: 10px;",
            ):
                for name in ["hover", "select", "click"]:
                    html.Option(name, value=name)

            html.Div(
                "{{ viewMode }} - {{ picking_modes }}",
                style="position: absolute; z-index: 10; top: 10px; left: 10px; color: white;",
            )

            with vtk_widgets.VtkRemoteLocalView(
                self.render_window,
                picking_modes=("picking_modes", []),
                select=(self.on_select, "[$event]"),
                hover=(self.on_hover, "[$event]"),
                click=(self.on_click, "[$event]"),
            ) as view:
                self.get_scene_object_id = view.get_scene_object_id
                print(view)


def main():
    app = PickingExample()
    app.server.start()


if __name__ == "__main__":
    main()
