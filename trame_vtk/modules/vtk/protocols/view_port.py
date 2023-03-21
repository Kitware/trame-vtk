from wslink import register as exportRpc

from .web_protocol import vtkWebProtocol


class vtkWebViewPort(vtkWebProtocol):
    """Basic 3D Viewport API (Camera + Orientation + CenterOfRotation"""

    @exportRpc("viewport.camera.reset")
    def resetCamera(self, viewId):
        """
        RPC callback to reset camera.
        """
        view = self.getView(viewId)
        renderer = view.GetRenderers().GetFirstRenderer()
        renderer.ResetCamera()

        self.getApplication().InvalidateCache(view)
        self.getApplication().InvokeEvent("UpdateEvent")

        return str(self.getGlobalId(view))

    @exportRpc("viewport.axes.orientation.visibility.update")
    def updateOrientationAxesVisibility(self, viewId, showAxis):
        """
        RPC callback to show/hide OrientationAxis.
        """
        view = self.getView(viewId)
        # FIXME seb: view.OrientationAxesVisibility = (showAxis if 1 else 0);

        self.getApplication().InvalidateCache(view)
        self.getApplication().InvokeEvent("UpdateEvent")

        return str(self.getGlobalId(view))

    @exportRpc("viewport.axes.center.visibility.update")
    def updateCenterAxesVisibility(self, viewId, showAxis):
        """
        RPC callback to show/hide CenterAxesVisibility.
        """
        view = self.getView(viewId)
        # FIXME seb: view.CenterAxesVisibility = (showAxis if 1 else 0);

        self.getApplication().InvalidateCache(view)
        self.getApplication().InvokeEvent("UpdateEvent")

        return str(self.getGlobalId(view))

    @exportRpc("viewport.camera.update")
    def updateCamera(self, view_id, focal_point, view_up, position, forceUpdate=True):
        view = self.getView(view_id)

        camera = view.GetRenderers().GetFirstRenderer().GetActiveCamera()
        camera.SetFocalPoint(focal_point)
        camera.SetViewUp(view_up)
        camera.SetPosition(position)

        if forceUpdate:
            self.getApplication().InvalidateCache(view)
            self.getApplication().InvokeEvent("UpdateEvent")
