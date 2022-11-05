from ..vtk.core import HybridView


def has_capabilities(*features):
    pass


class Helper:
    def __init__(self, app):
        self._root_protocol = None
        self._app = app
        self._hybrid_views = {}

        try:  # defer need to paraview to support --www usecase
            from paraview import servermanager
            from paraview.modules.vtkPVClientWeb import vtkPVWebApplication
            from vtkmodules.web.utils import mesh as mesh_vtk
        except ImportError:
            print("ParaView is not available")
        else:
            self._pv_core = vtkPVWebApplication()
            self._pv_core.SetImageEncoding(0)
            self._servermanager = servermanager
            self._mesh_vtk = mesh_vtk

            # Link our custom protocols initialization
            app.add_protocol_to_configure(self.configure_protocol)

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

    def scene(self, view_proxy, new_state=False):
        # flush data without requiring a render/picture
        tmp = view_proxy.SuppressRendering
        view_proxy.SuppressRendering = 1
        try:
            view_proxy.StillRender()
        finally:
            view_proxy.SuppressRendering = tmp

        return self._app.protocol_call(
            "viewport.geometry.view.get.state", self.id(view_proxy), new_state
        )

    def push_image(self, view_proxy, reset_camera=False):
        if view_proxy.EnableRenderOnInteraction:
            view_proxy.EnableRenderOnInteraction = 0

        if reset_camera:
            self._app.protocol_call(
                "viewport.camera.reset", {"view": self.id(view_proxy)}
            )

        return self._app.protocol_call(
            "viewport.image.push", {"view": self.id(view_proxy)}
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

    def configure_protocol(self, protocol):
        self._root_protocol = protocol

        from paraview.web.protocols import (
            ParaViewWebMouseHandler,
            ParaViewWebViewPort,
            ParaViewWebPublishImageDelivery,
            ParaViewWebLocalRendering,
        )
        from ..vtk.addon_serializer import registerAddOnSerializers

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

        # Add custom serializer ahead of proper vtk integration
        registerAddOnSerializers()

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


# -----------------------------------------------------------------------------
# Module advanced initialization
# -----------------------------------------------------------------------------

HELPER = None


def setup(app, **kwargs):
    global HELPER
    HELPER = Helper(app)


# -----------------------------------------------------------------------------
# Helper methods only valid once the module has been enabled
# -----------------------------------------------------------------------------


def id(vtk_obj):
    return HELPER.id(vtk_obj)


def object(vtk_id):
    return HELPER.object(vtk_id)


def mesh(dataset, field_to_keep=None, point_arrays=None, cell_arrays=None):
    return HELPER.mesh(dataset, field_to_keep, point_arrays, cell_arrays)


def scene(render_window, reset_camera=False, new_state=True):
    scene_state = HELPER.scene(render_window, new_state)
    if reset_camera:
        scene_state.setdefault("extra", {})["resetCamera"] = 1
    return scene_state


def push_image(render_window, reset_camera=False):
    return HELPER.push_image(render_window, reset_camera)


def camera(render_window):
    return HELPER.camera(render_window)


def set_camera(render_window, **kwargs):
    return HELPER.set_camera(render_window, **kwargs)


def view(view, name="view", **kwargs):
    return HELPER.add_hybrid_view(name, view, **kwargs)
