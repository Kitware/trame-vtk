from trame.app import get_server
from trame.widgets import vuetify, html, vtk as vtk_widgets
from trame.ui.vuetify import SinglePageLayout

from vtkmodules.vtkFiltersModeling import vtkOutlineFilter
from vtkmodules.vtkFiltersSources import vtkConeSource, vtkSphereSource
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

server = get_server()
server.client_type = "vue2"
state, ctrl = server.state, server.controller

state.trame__title = "Multi Local View"
state.view_names = ["blue", "red", "green", "gray"]
state.active_view = "blue"

# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

DEFAULT_RESOLUTION = 6
VIEWS = {}
COLORS = {
    "blue": (0, 0, 1),
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "gray": (0.5, 0.5, 0.5),
}


def create_pipeline(source):
    mapper = vtkPolyDataMapper()
    actor = vtkActor()
    if hasattr(source, "GetOutputPort"):
        mapper.SetInputConnection(source.GetOutputPort())
    else:
        mapper.SetInputData(source)
    actor.SetMapper(mapper)
    return actor


def create_vtk_view(color):
    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)

    renderer.SetBackground(COLORS[color])

    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    cone_source = vtkConeSource()
    cone_actor = create_pipeline(cone_source)
    renderer.AddActor(cone_actor)

    sphere_source = vtkSphereSource()
    sphere_actor = create_pipeline(sphere_source)
    renderer.AddActor(sphere_actor)

    # Dummy actor - to overcome the no-content issue
    filter = vtkOutlineFilter()
    filter.SetInputConnection(cone_source.GetOutputPort())
    renderer.AddActor(create_pipeline(filter))

    renderer.ResetCamera()
    renderWindow.Render()

    return dict(
        render_window=renderWindow,
        renderer=renderer,
        sphere=sphere_source,
        cone=cone_source,
        cone_actor=cone_actor,
        sphere_actor=sphere_actor,
        show_cone=True,
        show_sphere=True,
        resolution=DEFAULT_RESOLUTION,
        widget_on=True,
    )


# Create 4 views
for c in COLORS:
    VIEWS[c] = create_vtk_view(c)

# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@ctrl.set("update_active_view")
def update_active_view():
    ctrl[f"view_{state.active_view}_update"]()


@ctrl.set("reset_active_view")
def reset_active_view():
    ctrl[f"view_{state.active_view}_reset"]()


@state.change("active_view")
def active_view_change(active_view, **kwargs):
    pipeline = VIEWS[active_view]
    state.show_cone = pipeline.get("show_cone")
    state.show_sphere = pipeline.get("show_sphere")
    state.resolution = pipeline.get("resolution")
    state.widget_on = state[f"widget_on_{active_view}"]


@state.change("widget_on")
def toggle_view(widget_on, active_view, **kwargs):
    state[f"widget_on_{active_view}"] = widget_on


@state.change("resolution")
def update_resolution(resolution, active_view, **kwargs):
    pipeline = VIEWS[active_view]
    pipeline.get("cone").SetResolution(resolution)
    pipeline["resolution"] = resolution
    update_active_view()


def update_reset_resolution():
    state.resolution = DEFAULT_RESOLUTION


@state.change("show_cone")
def update_cone(active_view, show_cone, **kwargs):
    pipeline = VIEWS[active_view]
    renderer = pipeline.get("renderer")
    cone_actor = pipeline.get("cone_actor")
    pipeline["show_sphere"] = show_cone
    if show_cone:
        renderer.AddActor(cone_actor)
    else:
        renderer.RemoveActor(cone_actor)
    update_active_view()


@state.change("show_sphere")
def update_sphere(active_view, show_sphere, **kwargs):
    pipeline = VIEWS[active_view]
    renderer = pipeline.get("renderer")
    sphere_actor = pipeline.get("sphere_actor")
    pipeline["show_sphere"] = show_sphere
    if show_sphere:
        renderer.AddActor(sphere_actor)
    else:
        renderer.RemoveActor(sphere_actor)
    update_active_view()


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.icon.click = ctrl.reset_active_view
    layout.title.set_text("Local Rendering")

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            v_model=("active_view",),
            items=("view_names",),
            dense=True,
            hide_details=True,
            style="max-width: 200px;",
        )
        vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VSlider(
            v_model=("resolution", DEFAULT_RESOLUTION),
            min=3,
            max=60,
            step=1,
            hide_details=True,
            dense=True,
            style="max-width: 300px",
        )

        with vuetify.VBtn(icon=True, click=update_reset_resolution):
            vuetify.VIcon("mdi-undo-variant")

        vuetify.VDivider(vertical=True, classes="mx-2")

        with vuetify.VBtn(icon=True, click=ctrl.update_active_view):
            vuetify.VIcon("mdi-database-refresh-outline")

        vuetify.VDivider(vertical=True, classes="mx-2")

        vuetify.VCheckbox(
            v_model=("show_cone", True), label="Cone", dense=True, hide_details=True
        )
        vuetify.VCheckbox(
            v_model=("show_sphere", True), label="Sphere", dense=True, hide_details=True
        )
        vuetify.VDivider(vertical=True, classes="mx-2")
        vuetify.VCheckbox(
            v_model=("widget_on", True),
            dense=True,
            hide_details=True,
            on_icon="mdi-eye-outline",
            off_icon="mdi-eye-off-outline",
            classes="ml-4",
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
            style="display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr;",
        ):
            for c in COLORS:
                with html.Div(
                    style="height: 100%;justify-self: stretch;",
                    click=f"active_view = '{c}'",
                ):
                    render_window = VIEWS[c].get("render_window")
                    view = vtk_widgets.VtkLocalView(
                        render_window, v_if=(f"widget_on_{c}", True)
                    )
                    # view = vtk_widgets.VtkRemoteView(
                    #     render_window, v_if=(f"widget_on_{c}", True)
                    # )
                    ctrl[f"view_{c}_update"] = view.update
                    ctrl[f"view_{c}_reset"] = view.reset_camera


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
