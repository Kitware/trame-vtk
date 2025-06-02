from wslink import register as export_rpc

from .web_protocol import vtkWebProtocol


class vtkWebViewPort(vtkWebProtocol):
    """Basic 3_d Viewport API (Camera + Orientation + CenterOfRotation"""

    @export_rpc("viewport.camera.reset")
    def reset_camera(self, view_id):
        """
        RPC callback to reset camera.
        """
        view = self.get_view(view_id)
        renderer = view.GetRenderers().GetFirstRenderer()
        renderer.ResetCamera()

        self.app.InvalidateCache(view)
        self.app.InvokeEvent("UpdateEvent")

        return str(self.get_global_id(view))

    @export_rpc("viewport.axes.orientation.visibility.update")
    def update_orientation_axes_visibility(self, view_id, show_axis):
        """
        RPC callback to show/hide OrientationAxis.
        """
        view = self.get_view(view_id)
        # FIXME seb: view.OrientationAxesVisibility = (show_axis if 1 else 0);

        self.app.InvalidateCache(view)
        self.app.InvokeEvent("UpdateEvent")

        return str(self.get_global_id(view))

    @export_rpc("viewport.axes.center.visibility.update")
    def update_center_axes_visibility(self, view_id, show_axis):
        """
        RPC callback to show/hide CenterAxesVisibility.
        """
        view = self.get_view(view_id)
        # FIXME seb: view.CenterAxesVisibility = (show_axis if 1 else 0);

        self.app.InvalidateCache(view)
        self.app.InvokeEvent("UpdateEvent")

        return str(self.get_global_id(view))

    @export_rpc("viewport.camera.update")
    def update_camera(self, view_id, focal_point, view_up, position, force_update=True):
        view = self.get_view(view_id)

        camera = view.GetRenderers().GetFirstRenderer().GetActiveCamera()
        camera.SetFocalPoint(focal_point)
        camera.SetViewUp(view_up)
        camera.SetPosition(position)

        if force_update:
            self.app.InvalidateCache(view)
            self.app.InvokeEvent("UpdateEvent")
