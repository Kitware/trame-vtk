from paraview import simple
from wslink import register as exportRpc

from .web_protocol import ParaViewWebProtocol


class ParaViewWebViewPort(ParaViewWebProtocol):
    def __init__(self, scale=1.0, maxWidth=2560, maxHeight=1440, **kwargs):
        super(ParaViewWebViewPort, self).__init__()
        self.scale = scale
        self.maxWidth = maxWidth
        self.maxHeight = maxHeight

    # RpcName: resetCamera => viewport.camera.reset
    @exportRpc("viewport.camera.reset")
    def resetCamera(self, viewId):
        """
        RPC callback to reset camera.
        """
        view = self.getView(viewId)
        simple.Render(view)
        simple.ResetCamera(view)
        try:
            view.CenterOfRotation = view.CameraFocalPoint
        except AttributeError:
            pass

        self.getApplication().InvalidateCache(view.SMProxy)
        self.getApplication().InvokeEvent("UpdateEvent")

        return view.GetGlobalIDAsString()

    # RpcName: updateOrientationAxesVisibility => viewport.axes.orientation.visibility.update
    @exportRpc("viewport.axes.orientation.visibility.update")
    def updateOrientationAxesVisibility(self, viewId, showAxis):
        """
        RPC callback to show/hide OrientationAxis.
        """
        view = self.getView(viewId)
        view.OrientationAxesVisibility = showAxis if 1 else 0

        self.getApplication().InvalidateCache(view.SMProxy)
        self.getApplication().InvokeEvent("UpdateEvent")

        return view.GetGlobalIDAsString()

    # RpcName: updateCenterAxesVisibility => viewport.axes.center.visibility.update
    @exportRpc("viewport.axes.center.visibility.update")
    def updateCenterAxesVisibility(self, viewId, showAxis):
        """
        RPC callback to show/hide CenterAxesVisibility.
        """
        view = self.getView(viewId)
        view.CenterAxesVisibility = showAxis if 1 else 0

        self.getApplication().InvalidateCache(view.SMProxy)
        self.getApplication().InvokeEvent("UpdateEvent")

        return view.GetGlobalIDAsString()

    # RpcName: updateCamera => viewport.camera.update
    @exportRpc("viewport.camera.update")
    def updateCamera(self, view_id, focal_point, view_up, position, forceUpdate=True):
        view = self.getView(view_id)

        view.CameraFocalPoint = focal_point
        view.CameraViewUp = view_up
        view.CameraPosition = position

        if forceUpdate:
            self.getApplication().InvalidateCache(view.SMProxy)
            self.getApplication().InvokeEvent("UpdateEvent")

    @exportRpc("viewport.camera.get")
    def getCamera(self, view_id):
        view = self.getView(view_id)
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

    @exportRpc("viewport.size.update")
    def updateSize(self, view_id, width, height):
        view = self.getView(view_id)
        w = width * self.scale
        h = height * self.scale
        if w > self.maxWidth:
            s = float(self.maxWidth) / float(w)
            w *= s
            h *= s
        elif h > self.maxHeight:
            s = float(self.maxHeight) / float(h)
            w *= s
            h *= s
        view.ViewSize = [int(w), int(h)]
        self.getApplication().InvokeEvent("UpdateEvent")
