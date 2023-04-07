import warnings

from .core import HybridView
from .serializers import mesh as vtk_mesh

try:
    import vtkmodules  # noqa

    HAS_VTK = True
except ImportError:
    warnings.warn("VTK is not installed.")
    HAS_VTK = False

try:
    from vtkmodules.vtkWebCore import vtkWebApplication

    HAS_VTK_WEB = True
except ImportError:
    HAS_VTK_WEB = False

IMPROPER_VTK_MSG = """Your build of VTK does not have the proper web modules enabled.
These modules are typically enabled by default with the
`-DVTK_GROUP_ENABLE_Web:STRING=WANT` build flag.

Conda users: This is a known issue with the conda-forge VTK feedstock.
See https://github.com/conda-forge/vtk-feedstock/pull/258
"""


def has_capabilities(*features):
    if not HAS_VTK_WEB:
        raise ImportError(IMPROPER_VTK_MSG)


class Helper:
    def __init__(self, trame_server):
        self._root_protocol = None
        self._trame_server = trame_server
        if HAS_VTK_WEB:
            self._vtk_core = vtkWebApplication()
            self._vtk_core.SetImageEncoding(0)
            self._hybrid_views = {}

            # Link our custom protocols initialization
            trame_server.add_protocol_to_configure(self.configure_protocol)

    def id(self, vtk_obj):
        if not vtk_obj:
            return ""
        return str(self._vtk_core.GetObjectIdMap().GetGlobalId(vtk_obj))

    def object(self, vtk_id):
        return self._vtk_core.GetObjectIdMap().GetVTKObject(int(vtk_id))

    def mesh(self, dataset, field_to_keep=None, point_arrays=None, cell_arrays=None):
        if dataset.IsA("vtkAlgorithm"):
            dataset.Update()
            dataset = dataset.GetOutput()
        return vtk_mesh(
            dataset,
            field_to_keep=field_to_keep,
            point_arrays=point_arrays,
            cell_arrays=cell_arrays,
        )

    def scene(
        self, render_window, new_state=False, widgets=None, orientation_axis=0, **kwargs
    ):
        return self._trame_server.protocol_call(
            "viewport.geometry.view.get.state",
            self.id(render_window),
            new_state,
            widgets=widgets,
            orientation_axis=orientation_axis,
        )

    def export(self, render_window, widgets=None, orientation_axis=0, **kwargs):
        return self._trame_server.protocol_call(
            "viewport.geometry.view.get.export",
            self.id(render_window),
            widgets=widgets,
            orientation_axis=orientation_axis,
        )

    def push_image(self, render_window, reset_camera=False):
        # Disable any double render...
        render_window.GetInteractor().EnableRenderOff()

        if reset_camera:
            self._trame_server.protocol_call(
                "viewport.camera.reset", self.id(render_window)
            )

        return self._trame_server.protocol_call(
            "viewport.image.push", {"view": self.id(render_window)}
        )

    def camera(self, render_window):
        camera = render_window.GetRenderers().GetFirstRenderer().GetActiveCamera()
        return {
            "focalPoint": list(camera.GetFocalPoint()),
            "parallelProjection": camera.GetParallelProjection(),
            "parallelScale": camera.GetParallelScale(),
            "position": list(camera.GetPosition()),
            "viewAngle": camera.GetViewAngle(),
            "viewUp": list(camera.GetViewUp()),
            "centerOfRotation": list(camera.GetFocalPoint()),  # no center of rotation
        }

    def set_camera(self, render_window, **kwargs):
        camera = render_window.GetRenderers().GetFirstRenderer().GetActiveCamera()
        key_to_setter = {
            "focalPoint": "SetFocalPoint",
            "parallelProjection": "SetParallelProjection",
            "parallelScale": "SetParallelScale",
            "position": "SetPosition",
            "viewAngle": "SetViewAngle",
            "viewUp": "SetViewUp",
        }
        for key, setter in key_to_setter.items():
            if key in kwargs:
                getattr(camera, setter)(kwargs[key])

    def configure_protocol(self, protocol):
        self._root_protocol = protocol
        from .protocols import (
            vtkWebLocalRendering,
            vtkWebMouseHandler,
            vtkWebPublishImageDelivery,
            vtkWebViewPort,
        )

        # Initialize vtk application helper
        self._root_protocol.setSharedObject("app", self._vtk_core)

        # Remote rendering - image delivery
        self._root_protocol.registerLinkProtocol(vtkWebMouseHandler())
        self._root_protocol.registerLinkProtocol(vtkWebViewPort())
        self._root_protocol.registerLinkProtocol(
            vtkWebPublishImageDelivery(decode=False)
        )

        # Remote rendering - geometry delivery
        self._root_protocol.registerLinkProtocol(vtkWebLocalRendering())

    def add_hybrid_view(
        self,
        name,
        view,
        mode="local",
        interactive_ratio=1,
        interactive_quality=60,
        still_ratio=1,
        still_quality=98,
        force_replace=False,
        **kwargs,
    ):
        if name in self._hybrid_views:
            if force_replace:
                self._hybrid_views[name].replace_view(view)
            else:
                print(f"A view with name ({name}) is already registered")
                print(" => returning previous one")
            return self._hybrid_views[name]

        view_helper = HybridView(
            self,
            view,
            name,
            mode,
            interactive_ratio,
            interactive_quality,
            still_ratio,
            still_quality,
        )
        self._hybrid_views[name] = view_helper
        return view_helper

    def reload_app(self):
        self._hybrid_views = {}


# -----------------------------------------------------------------------------
# Module advanced initialization
# -----------------------------------------------------------------------------

HELPER = None


def setup(trame_server, **kwargs):
    global HELPER
    if HAS_VTK_WEB:
        HELPER = Helper(trame_server)


def reload_app():
    if HELPER:
        HELPER.reload_app()


# -----------------------------------------------------------------------------
# Helper methods only valid once the module has been enabled
# -----------------------------------------------------------------------------


def id(vtk_obj):
    return HELPER.id(vtk_obj)


def object(vtk_id):
    return HELPER.object(vtk_id)


def mesh(dataset, field_to_keep=None, point_arrays=None, cell_arrays=None):
    return HELPER.mesh(dataset, field_to_keep, point_arrays, cell_arrays)


def scene(
    render_window, reset_camera=False, new_state=True, widgets=None, orientation_axis=0
):
    scene_state = HELPER.scene(
        render_window, new_state, widgets=widgets, orientation_axis=orientation_axis
    )
    if reset_camera:
        scene_state.setdefault("extra", {})["resetCamera"] = 1
    return scene_state


def export(render_window, widgets=None, orientation_axis=0):
    return HELPER.export(
        render_window, widgets=widgets, orientation_axis=orientation_axis
    )


def push_image(render_window, reset_camera=False):
    return HELPER.push_image(render_window, reset_camera)


def camera(render_window):
    return HELPER.camera(render_window)


def set_camera(render_window, **kwargs):
    return HELPER.set_camera(render_window, **kwargs)


def view(view, name="view", **kwargs):
    return HELPER.add_hybrid_view(name, view, **kwargs)
