from paraview import simple
from wslink import register as export_rpc

from .web_protocol import ParaViewWebProtocol


class ParaViewWebViewPort(ParaViewWebProtocol):
    def __init__(self, scale=1.0, max_width=2560, max_height=1440, **kwargs):
        super().__init__()
        self.scale = scale
        self.max_width = max_width
        self.max_height = max_height

    # RpcName: reset_camera => viewport.camera.reset
    @export_rpc("viewport.camera.reset")
    def reset_camera(self, view_id):
        """
        RPC callback to reset camera.
        """
        view = self.get_view(view_id)
        simple.Render(view)
        simple.ResetCamera(view)
        try:
            view.CenterOfRotation = view.CameraFocalPoint
        except AttributeError:
            pass

        self.app.InvalidateCache(view.SMProxy)
        self.app.InvokeEvent("UpdateEvent")

        return view.GetGlobalIDAsString()

    # RpcName: update_orientation_axes_visibility => viewport.axes.orientation.visibility.update
    @export_rpc("viewport.axes.orientation.visibility.update")
    def update_orientation_axes_visibility(self, view_id, show_axis):
        """
        RPC callback to show/hide OrientationAxis.
        """
        view = self.get_view(view_id)
        view.OrientationAxesVisibility = show_axis if 1 else 0

        self.app.InvalidateCache(view.SMProxy)
        self.app.InvokeEvent("UpdateEvent")

        return view.GetGlobalIDAsString()

    # RpcName: update_center_axes_visibility => viewport.axes.center.visibility.update
    @export_rpc("viewport.axes.center.visibility.update")
    def update_center_axes_visibility(self, view_id, show_axis):
        """
        RPC callback to show/hide CenterAxesVisibility.
        """
        view = self.get_view(view_id)
        view.CenterAxesVisibility = show_axis if 1 else 0

        self.app.InvalidateCache(view.SMProxy)
        self.app.InvokeEvent("UpdateEvent")

        return view.GetGlobalIDAsString()

    # RpcName: update_camera => viewport.camera.update
    @export_rpc("viewport.camera.update")
    def update_camera(self, view_id, focal_point, view_up, position, force_update=True):
        view = self.get_view(view_id)

        view.CameraFocalPoint = focal_point
        view.CameraViewUp = view_up
        view.CameraPosition = position

        if force_update:
            self.app.InvalidateCache(view.SMProxy)
            self.app.InvokeEvent("UpdateEvent")

    @export_rpc("viewport.camera.get")
    def get_camera(self, view_id):
        view = self.get_view(view_id)
        bounds = [-1, 1, -1, 1, -1, 1]

        if view and view.GetClientSideView().GetClassName() == "vtkPVRenderView":
            rr = view.GetClientSideView().GetRenderer()
            bounds = rr.ComputeVisiblePropBounds()

        return {
            "bounds": bounds,
            "center": list(view.CenterOfRotation),
            "focal": list(view.CameraFocalPoint),
            "up": list(view.CameraViewUp),
            "position": list(view.CameraPosition),
        }

    @export_rpc("viewport.size.update")
    def update_size(self, view_id, width, height):
        view = self.get_view(view_id)
        w = width * self.scale
        h = height * self.scale
        if w > self.max_width:
            s = float(self.max_width) / float(w)
            w *= s
            h *= s
        elif h > self.max_height:
            s = float(self.max_height) / float(h)
            w *= s
            h *= s
        view.ViewSize = [int(w), int(h)]
        self.app.InvokeEvent("UpdateEvent")
