from trame.app import get_server
from trame.ui.html import DivLayout
from vtk import mutable
from vtkmodules.vtkCommonDataModel import vtkCellLocator
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
)

from trame.widgets import client, html
from trame.widgets import vtk as vtk_widgets


class PickingExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")

        # VTK
        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)

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

        self.vtk_mapping = {
            self.get_scene_object_id(cone_actor): "Cone",
            self.get_scene_object_id(sphere_actor): "Sphere",
        }

        self.remote_id_to_actor = {
            self.get_scene_object_id(cone_actor): cone_actor,
            self.get_scene_object_id(sphere_actor): sphere_actor,
        }

        self.actor_remote_id_to_locator = {}

    def on_click(self, event):
        if event is None:
            print("Click on: --nothing--")
        else:
            remote_id = event.get("remoteId")
            print(f"Click on: {self.vtk_mapping.get(remote_id)}")

            cell_locator = self.actor_remote_id_to_locator.get(remote_id)

            if not cell_locator:
                cell_locator = vtkCellLocator()
                self.actor_remote_id_to_locator[remote_id] = cell_locator
                actor = self.remote_id_to_actor[remote_id]
                cell_locator.SetDataSet(actor.GetMapper().GetInputDataObject(0, 0))

            world_position = event.get("worldPosition")
            closes_point = [0.0, 0.0, 0.0]

            _subId = mutable(0)
            _dist2 = mutable(0.0)
            cell_id = mutable(-1)
            cell_locator.FindClosestPoint(
                world_position, closes_point, cell_id, _subId, _dist2
            )

            print(f"picked {cell_id=}")

    def on_select(self, event):
        print(
            "Selected:",
            [self.vtk_mapping.get(actor_id) for actor_id in event.get("remoteIds")],
        )

    def on_hover(self, event):
        if event:
            print(f"Hover on: {self.vtk_mapping.get(event.get('remoteId'))}")

    def _build_ui(self):
        with DivLayout(self.server) as layout:
            client.Style("html, body { padding: 0; margin: 0; }")
            layout.root.style = "width: 100vw; height: 100vh;"

            with html.Select(
                v_model="picking_modes",
                multiple=True,
                style="position: absolute; z-index: 10; top: 10px; right: 10px;",
            ):
                for name in ["hover", "select", "click"]:
                    html.Option(name, value=name)

            html.Div(
                "{{ picking_modes }}",
                style="position: absolute; z-index: 10; top: 10px; left: 10px; color: white;",
            )

            with vtk_widgets.VtkLocalView(
                self.render_window,
                picking_modes=("picking_modes", []),
                select=(self.on_select, "[$event]"),
                hover=(self.on_hover, "[$event]"),
                click=(self.on_click, "[$event]"),
            ) as view:
                self.get_scene_object_id = view.get_scene_object_id


def main():
    app = PickingExample()
    app.server.start()


if __name__ == "__main__":
    main()
