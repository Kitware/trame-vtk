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

from trame_vtk.modules.vtk.serializers.utils import reference_id

INTERACTOR_SETTINGS_WITH_SELECT = [
    {
        "button": 1,
        "action": "Rotate",
    },
    {
        "button": 2,
        "action": "Pan",
    },
    {
        "button": 3,
        "action": "Zoom",
        "scrollEnabled": True,
    },
    {
        "button": 1,
        "action": "Pan",
        "alt": True,
    },
    {
        "button": 1,
        "action": "Zoom",
        "control": True,
    },
    {
        "button": 1,
        "action": "Select",
        "shift": True,
    },
    {
        "button": 1,
        "action": "Roll",
        "alt": True,
        "shift": True,
    },
]


class PickingExample:
    def __init__(self, server=None):
        self.server = get_server(server, client_type="vue3")
        self._hover_something = False

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

        self.id_to_actor_name = {
            reference_id(cone_actor): "Cone",
            reference_id(sphere_actor): "Sphere",
        }

        # Configure hardware selector for actor picking
        self.select.SetFieldAssociation(vtkDataObject.FIELD_ASSOCIATION_CELLS)
        self.select.SetRenderer(renderer)
        self.select.SetActorPassOnly(True)

        # UI
        self.ui = self._build_ui()

    def _get_name_from_refid(self, ref_id):
        return self.id_to_actor_name.get(ref_id)

    def _get_name_from_actor(self, actor):
        return self._get_name_from_refid(reference_id(actor))

    def _get_picked_actor(self, position):
        self.picker.Pick(position.get("x"), position.get("y"), 0, self.renderer)
        return self.picker.GetActor()

    def on_click(self, event):
        mode = "local"
        name = "Nothing"
        if event:
            mode = event.get("mode")
            if mode == "local":
                name = self._get_name_from_refid(event.get("remoteId"))
            elif mode == "remote":
                actor = self._get_picked_actor(event.get("position"))
                name = self._get_name_from_actor(actor)

        print(f"Clicked on {name} - {mode=}")

    def on_select(self, event):
        mode = event.get("mode", "local")
        names = []
        if mode == "local":
            names = [self._get_name_from_refid(rid) for rid in event.get("remoteIds")]
        elif mode == "remote":
            x_min, x_max, y_min, y_max = event.get("selection")
            self.select.SetArea(int(x_min), int(y_min), int(x_max), int(y_max))
            selection = self.select.Select()
            nb_selections = selection.GetNumberOfNodes()
            for i in range(nb_selections):
                node = selection.GetNode(i)
                actor = node.GetProperties().Get(node.PROP())
                names.append(self._get_name_from_actor(actor))

        print(f"Selecting ({mode=}): {names}")

    def on_hover(self, event):
        if event is None:
            if self._hover_something:
                self._hover_something = False
                print("Hover nothing - mode=local")

            return

        name = "Nothing"
        mode = event.get("mode")
        if mode == "local":
            self._hover_something = True
            name = self._get_name_from_refid(event.get("remoteId"))
        elif mode == "remote":
            actor = self._get_picked_actor(event.get("position"))
            name = self._get_name_from_actor(actor)
            self._hover_something = name is not None

        print(f"Hovering on {name} - {mode=}")

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
                interactor_settings=("settings", INTERACTOR_SETTINGS_WITH_SELECT),
            ) as view:
                self.get_scene_object_id = view.get_scene_object_id


def main():
    app = PickingExample()
    app.server.start()


if __name__ == "__main__":
    main()
