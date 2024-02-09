from trame.app import get_server
from trame.ui.html import DivLayout
from trame.widgets import html, client, vtk as vtk_widgets

from vtkmodules.vtkCommonDataModel import vtkDataObject
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPolyDataMapper,
    vtkActor,
    vtkPropPicker,
    vtkHardwareSelector,
)

from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa
import vtkmodules.vtkRenderingOpenGL2  # noqa


class PickingExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")
        self.active_selection = False

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
        self.picker = vtkPropPicker()
        self.select = vtkHardwareSelector()
        self.renderer = renderer
        self.actor_map = {
            "Sphere": sphere_actor,
            "Cone": cone_actor,
        }

        # Configure hardware selector for actor picking
        self.select.SetFieldAssociation(vtkDataObject.FIELD_ASSOCIATION_CELLS)
        self.select.SetRenderer(renderer)
        self.select.SetActorPassOnly(True)

        # UI
        self.ui = self._build_ui()

    def _find_actor_name(self, actor):
        if actor:
            for name, a in self.actor_map.items():
                if a == actor:
                    return name
        return None

    def _get_picked_actor_name(self, position):
        self.picker.Pick(position.get("x"), position.get("y"), 0, self.renderer)
        return self._find_actor_name(self.picker.GetActor())

    def on_click(self, event):
        selected_actor_name = self._get_picked_actor_name(event.get("position"))
        if selected_actor_name:
            print(f"Clicked {selected_actor_name}")
        else:
            print("Clicked -- nothing")

    def on_select(self, event):
        x_min, x_max, y_min, y_max = event.get("selection")
        self.select.SetArea(int(x_min), int(y_min), int(x_max), int(y_max))
        selection = self.select.Select()
        nb_selections = selection.GetNumberOfNodes()
        for i in range(nb_selections):
            node = selection.GetNode(i)
            actor = node.GetProperties().Get(node.PROP())
            print(f"selected: {self._find_actor_name(actor)}")

        if nb_selections == 0:
            print("No actor selected")

    def on_hover(self, event):
        selected_actor_name = self._get_picked_actor_name(event.get("position"))
        if selected_actor_name:
            self.active_selection = True
            print(f"Hover {selected_actor_name}")
        elif self.active_selection:
            self.active_selection = False
            print("Hover -- exited actor")

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

            with vtk_widgets.VtkRemoteView(
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
