from wslink import register as exportRpc

from .serializers import (
    serializeInstance,
    SynchronizationContext,
    getReferenceId,
    initializeSerializers,
)
from .web_protocol import vtkWebProtocol


class vtkWebLocalRendering(vtkWebProtocol):
    """Improved geometry delivery for client-side rendering

    Provide an updated geometry delivery mechanism which better matches the
    client-side rendering capability we have in vtk.js
    """

    def __init__(self, **kwargs):
        super(vtkWebLocalRendering, self).__init__()
        initializeSerializers()
        self.context = SynchronizationContext()
        self.trackingViews = {}
        self.mtime = 0

    # RpcName: getArray => viewport.geometry.array.get
    @exportRpc("viewport.geometry.array.get")
    def getArray(self, dataHash, binary=False):
        if binary:
            return self.addAttachment(self.context.getCachedDataArray(dataHash, binary))
        return self.context.getCachedDataArray(dataHash, binary)

    # RpcName: addViewObserver => viewport.geometry.view.observer.add
    @exportRpc("viewport.geometry.view.observer.add")
    def addViewObserver(self, viewId):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = self.getApplication().GetObjectIdMap().GetGlobalId(sView)

        def pushGeometry(newSubscription=False):
            stateToReturn = self.getViewState(realViewId, newSubscription)
            stateToReturn["mtime"] = 0 if newSubscription else self.mtime
            self.mtime += 1
            return stateToReturn

        if realViewId not in self.trackingViews:
            observerCallback = lambda *args, **kwargs: self.publish(
                "viewport.geometry.view.subscription", pushGeometry()
            )
            tag = self.getApplication().AddObserver("UpdateEvent", observerCallback)
            self.trackingViews[realViewId] = {"tags": [tag], "observerCount": 1}
        else:
            # There is an observer on this view already
            self.trackingViews[realViewId]["observerCount"] += 1

        self.publish("viewport.geometry.view.subscription", pushGeometry(True))
        return {"success": True, "viewId": realViewId}

    # RpcName: removeViewObserver => viewport.geometry.view.observer.remove
    @exportRpc("viewport.geometry.view.observer.remove")
    def removeViewObserver(self, viewId):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = self.getApplication().GetObjectIdMap().GetGlobalId(sView)

        observerInfo = None
        if realViewId in self.trackingViews:
            observerInfo = self.trackingViews[realViewId]

        if not observerInfo:
            return {"error": "Unable to find subscription for view %s" % realViewId}

        observerInfo["observerCount"] -= 1

        if observerInfo["observerCount"] <= 0:
            for tag in observerInfo["tags"]:
                self.getApplication().RemoveObserver(tag)
            del self.trackingViews[realViewId]

        return {"result": "success"}

    # RpcName: getViewState => viewport.geometry.view.get.state
    @exportRpc("viewport.geometry.view.get.state")
    def getViewState(self, viewId, newSubscription=False):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        self.context.setIgnoreLastDependencies(newSubscription)

        # Get the active view and render window, use it to iterate over renderers
        renderWindow = sView
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        renderWindowId = self.getApplication().GetObjectIdMap().GetGlobalId(sView)
        viewInstance = serializeInstance(
            None, renderWindow, renderWindowId, self.context, 1
        )
        viewInstance["extra"] = {
            "vtkRefId": getReferenceId(renderWindow),
            "centerOfRotation": camera.GetFocalPoint(),
            "camera": getReferenceId(camera),
        }

        self.context.setIgnoreLastDependencies(False)
        self.context.checkForArraysToRelease()

        if viewInstance:
            return viewInstance

        return None
