import logging

from ..vtk.core import HybridView
from ..vtk.serializers.mesh import mesh as mesh_vtk

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def has_capabilities(*features):
    pass


class Helper:
    def __init__(self, trame_server):
        self._root_protocol = None
        self._trame_server = trame_server
        self._hybrid_views = {}

        try:  # defer need to paraview to support --www usecase
            from paraview import servermanager
            from paraview.modules.vtkPVClientWeb import vtkPVWebApplication
        except ImportError:
            logger.exception("*** ERROR: ParaView is not available!")
        else:
            self._pv_core = vtkPVWebApplication()
            self._pv_core.SetImageEncoding(0)
            self._servermanager = servermanager
            self._mesh_vtk = mesh_vtk

            # Link our custom protocols initialization
            trame_server.add_protocol_to_configure(self.configure_protocol)

    def has_capabilities(self, *features):
        has_capabilities(*features)

    def id(self, pv_proxy):
        if pv_proxy:
            return pv_proxy.GetGlobalIDAsString()
        return ""

    def object(self, pv_id):
        try:
            pv_id = int(pv_id)
        except ValueError:
            return None
        if pv_id <= 0:
            return None
        return self._servermanager._getPyProxy(
            self._servermanager.ActiveConnection.Session.GetRemoteObject(pv_id)
        )

    def mesh(self, proxy, field_to_keep=None, point_arrays=None, cell_arrays=None):
        proxy.UpdatePipeline()
        source = proxy.GetClientSideObject()
        dataset = source.GetOutput()
        return self._mesh_vtk(
            dataset,
            field_to_keep=field_to_keep,
            point_arrays=point_arrays,
            cell_arrays=cell_arrays,
        )

    def scene(
        self,
        view_proxy,
        reset_camera=False,
        new_state=False,
        widgets=None,
        orientation_axis=0,
        **kwargs,
    ):
        # flush data without requiring a render/picture
        tmp = view_proxy.SuppressRendering
        view_proxy.SuppressRendering = 1
        try:
            view_proxy.StillRender()
        finally:
            view_proxy.SuppressRendering = tmp

        scene_state = self._trame_server.protocol_call(
            "viewport.geometry.view.get.state",
            self.id(view_proxy),
            new_state,
            widgets=widgets,
            orientation_axis=orientation_axis,
        )
        if reset_camera:
            scene_state.setdefault("extra", {})["resetCamera"] = 1
        return scene_state

    def export(self, render_window, widgets=None, orientation_axis=0, **kwargs):
        return self._trame_server.protocol_call(
            "viewport.geometry.view.get.export",
            self.id(render_window),
            widgets=widgets,
            orientation_axis=orientation_axis,
        )

    def push_image(self, view_proxy, reset_camera=False):
        if view_proxy.GetPropertyValue("EnableRenderOnInteraction"):
            view_proxy.EnableRenderOnInteraction = 0

        if reset_camera:
            self._trame_server.protocol_call(
                "viewport.camera.reset", self.id(view_proxy)
            )

        return self._trame_server.protocol_call(
            "viewport.image.push", {"view": self.id(view_proxy)}
        )

    def get_current_image_quality(self, render_window):
        return self._trame_server.protocol_call(
            "viewport.image.push.quality.get", self.id(render_window)
        )

    def set_image_quality(self, render_window, quality, ratio):
        self._trame_server.protocol_call(
            "viewport.image.push.quality",
            self.id(render_window),
            quality,
            ratio,
        )

    def start_animation(self, render_window, fps=30, quality=100, ratio=1):
        self._trame_server.protocol_call("viewport.image.animation.fps.max", fps)
        self.set_image_quality(render_window, quality, ratio)
        self._trame_server.protocol_call(
            "viewport.image.animation.start", self.id(render_window)
        )

    def stop_animation(self, render_window):
        self._trame_server.protocol_call(
            "viewport.image.animation.stop", self.id(render_window)
        )

    def camera(self, view_proxy):
        view_proxy.UpdatePropertyInformation()
        return {
            "focalPoint": list(view_proxy.CameraFocalPoint),
            "parallelProjection": view_proxy.CameraParallelProjection,
            "parallelScale": view_proxy.CameraParallelScale,
            "position": list(view_proxy.CameraPosition),
            "viewAngle": view_proxy.CameraViewAngle,
            "viewUp": list(view_proxy.CameraViewUp),
            "centerOfRotation": list(view_proxy.CenterOfRotation),
        }

    def set_camera(self, view_proxy, **kwargs):
        key_to_attr = {
            "focalPoint": "CameraFocalPoint",
            "parallelProjection": "CameraParallelProjection",
            "parallelScale": "CameraParallelScale",
            "position": "CameraPosition",
            "viewAngle": "CameraViewAngle",
            "viewUp": "CameraViewUp",
            "centerOfRotation": "CenterOfRotation",
        }

        for key, attr in key_to_attr.items():
            if key in kwargs:
                setattr(view_proxy, attr, kwargs[key])

    def view(self, view_proxy, name="view", **kwargs):
        return self.add_hybrid_view(name, view_proxy, **kwargs)

    def configure_protocol(self, protocol):
        self._root_protocol = protocol

        from .protocols import (
            ParaViewWebLocalRendering,
            ParaViewWebMouseHandler,
            ParaViewWebPublishImageDelivery,
            ParaViewWebViewPort,
        )

        # Initialize vtk application helper
        self._root_protocol.setSharedObject("app", self._pv_core)

        # Remote rendering - image delivery
        self._root_protocol.registerLinkProtocol(ParaViewWebMouseHandler())
        self._root_protocol.registerLinkProtocol(ParaViewWebViewPort())
        self._root_protocol.registerLinkProtocol(
            ParaViewWebPublishImageDelivery(decode=False)
        )

        # Remote rendering - geometry delivery
        self._root_protocol.registerLinkProtocol(ParaViewWebLocalRendering())

        # Mimic client interactor on server side
        from .core import apply_default_interaction_settings

        apply_default_interaction_settings()

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

    def remove_hybrid_view(self, name):
        if name in self._hybrid_views:
            self._hybrid_views.pop(name)


# -----------------------------------------------------------------------------
# Module advanced initialization
# -----------------------------------------------------------------------------
HELPERS_PER_SERVER = {}


def setup(trame_server, **kwargs):
    global HELPERS_PER_SERVER
    HELPERS_PER_SERVER[trame_server.name] = Helper(trame_server)


def get_helper(server):
    return HELPERS_PER_SERVER.get(server.name)
