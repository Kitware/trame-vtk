import base64
import time

from paraview import simple
from wslink import register as exportRpc
from wslink import schedule_callback

from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from .web_protocol import ParaViewWebProtocol


class ParaViewWebPublishImageDelivery(ParaViewWebProtocol):
    def __init__(self, decode=True, **kwargs):
        ParaViewWebProtocol.__init__(self)
        self.trackingViews = {}
        self.lastStaleTime = {}
        self.staleHandlerCount = {}
        self.deltaStaleTimeBeforeRender = 0.1  # 0.1s
        self.staleCountLimit = 10
        self.decode = decode
        self.viewsInAnimations = []
        self.targetFrameRate = 30.0
        self.minFrameRate = 12.0
        self.maxFrameRate = 30.0

        # Camera link handling
        self.linkedViews = []
        self.linkNames = []
        self.onLinkChange = None

        # Mouse handling
        self.lastAction = "up"
        self.activeViewId = None

    # In case some external protocol wants to monitor when link views change
    def setLinkChangeCallback(self, fn):
        self.onLinkChange = fn

    def pushRender(self, vId, ignoreAnimation=False, staleCount=0):
        if vId not in self.trackingViews:
            return

        if not self.trackingViews[vId]["enabled"]:
            return

        if not ignoreAnimation and len(self.viewsInAnimations) > 0:
            return

        if "originalSize" not in self.trackingViews[vId]:
            view = self.getView(vId)
            self.trackingViews[vId]["originalSize"] = (
                int(view.ViewSize[0]),
                int(view.ViewSize[1]),
            )

        if "ratio" not in self.trackingViews[vId]:
            self.trackingViews[vId]["ratio"] = 1

        ratio = self.trackingViews[vId]["ratio"]
        mtime = self.trackingViews[vId]["mtime"]
        quality = self.trackingViews[vId]["quality"]
        size = [int(s * ratio) for s in self.trackingViews[vId]["originalSize"]]

        reply = self.stillRender(
            {"view": vId, "mtime": mtime, "quality": quality, "size": size}
        )

        # View might have been deleted
        if not reply:
            return

        stale = reply["stale"]
        if reply["image"]:
            # depending on whether the app has encoding enabled:
            if self.decode:
                reply["image"] = base64.standard_b64decode(reply["image"])

            reply["image"] = self.addAttachment(reply["image"])
            reply["format"] = "jpeg"
            # save mtime for next call.
            self.trackingViews[vId]["mtime"] = reply["mtime"]
            # echo back real ID, instead of -1 for 'active'
            reply["id"] = vId
            self.publish("viewport.image.push.subscription", reply)
        if stale:
            self.lastStaleTime[vId] = time.time()
            if self.staleHandlerCount[vId] == 0:
                self.staleHandlerCount[vId] += 1
                schedule_callback(
                    self.deltaStaleTimeBeforeRender,
                    lambda: self.renderStaleImage(vId, staleCount),
                )
        else:
            self.lastStaleTime[vId] = 0

    def renderStaleImage(self, vId, staleCount=0):
        if vId in self.staleHandlerCount and self.staleHandlerCount[vId] > 0:
            self.staleHandlerCount[vId] -= 1

            if self.lastStaleTime[vId] != 0:
                delta = time.time() - self.lastStaleTime[vId]
                # Break on staleCount otherwise linked view will always report to be stale
                # And loop forever
                if (
                    delta >= (self.deltaStaleTimeBeforeRender * (staleCount + 1))
                    and staleCount < self.staleCountLimit
                ):
                    self.pushRender(vId, False, staleCount + 1)
                elif delta < self.deltaStaleTimeBeforeRender:
                    self.staleHandlerCount[vId] += 1
                    schedule_callback(
                        self.deltaStaleTimeBeforeRender - delta + 0.001,
                        lambda: self.renderStaleImage(vId, staleCount),
                    )

    def animate(self, renderAllViews=True):
        if len(self.viewsInAnimations) == 0:
            return

        nextAnimateTime = time.time() + 1.0 / self.targetFrameRate

        # Handle the rendering of the views
        if self.activeViewId:
            self.pushRender(self.activeViewId, True)

        if renderAllViews:
            for vId in set(self.viewsInAnimations):
                if vId != self.activeViewId:
                    self.pushRender(vId, True)

        nextAnimateTime -= time.time()

        if self.targetFrameRate > self.maxFrameRate:
            self.targetFrameRate = self.maxFrameRate

        if nextAnimateTime < 0:
            if nextAnimateTime < -1.0:
                self.targetFrameRate = 1
            if self.targetFrameRate > self.minFrameRate:
                self.targetFrameRate -= 1.0
            if self.activeViewId:
                # If active view, prioritize that one over the others
                # -> Divide by 2 the refresh rate of the other views
                schedule_callback(0.001, lambda: self.animate(not renderAllViews))
            else:
                # Keep animating at the best rate we can
                schedule_callback(0.001, lambda: self.animate())
        else:
            # We have time so let's render all
            if self.targetFrameRate < self.maxFrameRate and nextAnimateTime > 0.005:
                self.targetFrameRate += 1.0
            schedule_callback(nextAnimateTime, lambda: self.animate())

    @exportRpc("viewport.image.animation.fps.max")
    def setMaxFrameRate(self, fps=30):
        self.maxFrameRate = fps

    @exportRpc("viewport.image.animation.fps.get")
    def getCurrentFrameRate(self):
        return self.targetFrameRate

    @exportRpc("viewport.image.animation.start")
    def startViewAnimation(self, viewId="-1"):
        sView = self.getView(viewId)
        realViewId = sView.GetGlobalIDAsString()

        self.viewsInAnimations.append(realViewId)
        if len(self.viewsInAnimations) == 1:
            self.animate()

    @exportRpc("viewport.image.animation.stop")
    def stopViewAnimation(self, viewId="-1"):
        sView = self.getView(viewId)
        realViewId = sView.GetGlobalIDAsString()

        if realViewId in self.viewsInAnimations and realViewId in self.trackingViews:
            progressRendering = self.trackingViews[realViewId]["streaming"]
            self.viewsInAnimations.remove(realViewId)
            if progressRendering:
                self.progressiveRender(realViewId)

    def progressiveRender(self, viewId="-1"):
        sView = self.getView(viewId)
        realViewId = sView.GetGlobalIDAsString()

        if realViewId in self.viewsInAnimations:
            return

        if sView.GetSession().GetPendingProgress():
            schedule_callback(
                self.deltaStaleTimeBeforeRender, lambda: self.progressiveRender(viewId)
            )
        else:
            again = sView.StreamingUpdate(True)
            self.pushRender(realViewId, True)

            if again:
                schedule_callback(0.001, lambda: self.progressiveRender(viewId))

    @exportRpc("viewport.image.push")
    def imagePush(self, options):
        view = self.getView(options["view"])
        viewId = view.GetGlobalIDAsString()

        # Make sure an image is pushed
        self.getApplication().InvalidateCache(view.SMProxy)

        self.pushRender(viewId)

    # Internal function since the reply[image] is not
    # JSON(serializable) it can not be an RPC one
    def stillRender(self, options):
        """
        RPC Callback to render a view and obtain the rendered image.
        """
        beginTime = int(round(time.time() * 1000))
        viewId = str(options["view"])
        view = self.getView(viewId)

        # If no view id provided, skip rendering
        if not viewId:
            print("No view")
            print(options)
            return None

        # Make sure request match our selected view
        if viewId != "-1" and view.GetGlobalIDAsString() != viewId:
            # We got active view rather than our request
            view = None

        # No view to render => need some cleanup
        if not view:
            # The view has been deleted, we can not render it...
            # Clean up old view state
            if viewId in self.viewsInAnimations:
                self.viewsInAnimations.remove(viewId)

            if viewId in self.trackingViews:
                del self.trackingViews[viewId]

            if viewId in self.staleHandlerCount:
                del self.staleHandlerCount[viewId]

            # the view does not exist anymore, skip rendering
            return None

        # We are in business to render our view...

        # Make sure our view size match our request
        size = view.ViewSize[0:2]
        resize = size != options.get("size", size)
        if resize:
            size = options["size"]
            if size[0] > 10 and size[1] > 10:
                view.ViewSize = size

        # Rendering options
        t = 0
        if options and "mtime" in options:
            t = options["mtime"]
        quality = 100
        if options and "quality" in options:
            quality = options["quality"]
        localTime = 0
        if options and "localTime" in options:
            localTime = options["localTime"]
        reply = {}
        app = self.getApplication()
        if t == 0:
            app.InvalidateCache(view.SMProxy)
        if self.decode:
            stillRender = app.StillRenderToString
        else:
            stillRender = app.StillRenderToBuffer
        reply_image = stillRender(view.SMProxy, t, quality)

        # Check that we are getting image size we have set if not wait until we
        # do. The render call will set the actual window size.
        tries = 10
        while (
            resize
            and list(app.GetLastStillRenderImageSize()) != size
            and size != [0, 0]
            and tries > 0
        ):
            app.InvalidateCache(view.SMProxy)
            reply_image = stillRender(view.SMProxy, t, quality)
            tries -= 1

        if (
            not resize
            and options
            and ("clearCache" in options)
            and options["clearCache"]
        ):
            app.InvalidateCache(view.SMProxy)
            reply_image = stillRender(view.SMProxy, t, quality)

        # Pack the result
        reply["stale"] = app.GetHasImagesBeingProcessed(view.SMProxy)
        reply["mtime"] = app.GetLastStillRenderToMTime()
        reply["size"] = view.ViewSize[0:2]
        reply["memsize"] = reply_image.GetDataSize() if reply_image else 0
        reply["format"] = "jpeg;base64" if self.decode else "jpeg"
        reply["global_id"] = view.GetGlobalIDAsString()
        reply["localTime"] = localTime
        if self.decode:
            reply["image"] = reply_image
        else:
            # Convert the vtkUnsignedCharArray into a bytes object, required by Autobahn websockets
            reply["image"] = memoryview(reply_image).tobytes() if reply_image else None

        endTime = int(round(time.time() * 1000))
        reply["workTime"] = endTime - beginTime

        return reply

    @exportRpc("viewport.image.push.observer.add")
    def addRenderObserver(self, viewId):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = sView.GetGlobalIDAsString()

        if realViewId not in self.trackingViews:
            observerCallback = lambda *args, **kwargs: self.pushRender(realViewId)
            startCallback = lambda *args, **kwargs: self.startViewAnimation(realViewId)
            stopCallback = lambda *args, **kwargs: self.stopViewAnimation(realViewId)
            tag = self.getApplication().AddObserver("UpdateEvent", observerCallback)
            tagStart = self.getApplication().AddObserver(
                "StartInteractionEvent", startCallback
            )
            tagStop = self.getApplication().AddObserver(
                "EndInteractionEvent", stopCallback
            )
            # TODO do we need self.getApplication().AddObserver('ResetActiveView', resetActiveView())
            self.trackingViews[realViewId] = {
                "tags": [tag, tagStart, tagStop],
                "observerCount": 1,
                "mtime": 0,
                "enabled": True,
                "quality": 100,
                "streaming": sView.GetClientSideObject().GetEnableStreaming(),
            }
            self.staleHandlerCount[realViewId] = 0
        else:
            # There is an observer on this view already
            self.trackingViews[realViewId]["observerCount"] += 1

        self.pushRender(realViewId)
        return {"success": True, "viewId": realViewId}

    @exportRpc("viewport.image.push.observer.remove")
    def removeRenderObserver(self, viewId):
        sView = None
        try:
            sView = self.getView(viewId)
        except Exception:
            print("no view with ID %s available in removeRenderObserver" % viewId)

        realViewId = sView.GetGlobalIDAsString() if sView else viewId

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
            del self.staleHandlerCount[realViewId]

        return {"result": "success"}

    @exportRpc("viewport.image.push.quality")
    def setViewQuality(self, viewId, quality, ratio=1, updateLinkedView=True):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = sView.GetGlobalIDAsString()
        observerInfo = None
        if realViewId in self.trackingViews:
            observerInfo = self.trackingViews[realViewId]

        if not observerInfo:
            return {"error": "Unable to find subscription for view %s" % realViewId}

        observerInfo["quality"] = quality
        observerInfo["ratio"] = ratio

        # Handle linked view quality/ratio synch
        if updateLinkedView and realViewId in self.linkedViews:
            for vid in self.linkedViews:
                self.setViewQuality(vid, quality, ratio, False)

        # Update image size right now!
        if "originalSize" in self.trackingViews[realViewId]:
            size = [
                int(s * ratio) for s in self.trackingViews[realViewId]["originalSize"]
            ]
            if "SetSize" in sView:
                sView.SetSize(size)
            else:
                sView.ViewSize = size

        return {"result": "success"}

    @exportRpc("viewport.image.push.original.size")
    def setViewSize(self, viewId, width, height):
        if width < 10 or height < 10:
            return {"result": "size skip"}

        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = sView.GetGlobalIDAsString()
        observerInfo = None
        if realViewId in self.trackingViews:
            observerInfo = self.trackingViews[realViewId]

        if not observerInfo:
            return {"error": "Unable to find subscription for view %s" % realViewId}

        observerInfo["originalSize"] = (int(width), int(height))

        return {"result": "success"}

    @exportRpc("viewport.image.push.enabled")
    def enableView(self, viewId, enabled):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = sView.GetGlobalIDAsString()
        observerInfo = None
        if realViewId in self.trackingViews:
            observerInfo = self.trackingViews[realViewId]

        if not observerInfo:
            return {"error": "Unable to find subscription for view %s" % realViewId}

        observerInfo["enabled"] = enabled

        return {"result": "success"}

    @exportRpc("viewport.image.push.invalidate.cache")
    def invalidateCache(self, viewId):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        self.getApplication().InvalidateCache(sView.SMProxy)
        self.getApplication().InvokeEvent("UpdateEvent")
        return {"result": "success"}

    # -------------------------------------------------------------------------
    # View linked
    # -------------------------------------------------------------------------

    def validateViewLinks(self):
        for linkName in self.linkNames:
            simple.RemoveCameraLink(linkName)
        self.linkNames = []

        if len(self.linkedViews) > 1:
            viewList = [self.getView(vid) for vid in self.linkedViews]
            refView = viewList.pop(0)
            for view in viewList:
                linkName = "%s_%s" % (
                    refView.GetGlobalIDAsString(),
                    view.GetGlobalIDAsString(),
                )
                simple.AddCameraLink(refView, view, linkName)
                self.linkNames.append(linkName)

            # Synch camera state
            srcView = viewList[0]
            dstViews = viewList[1:]
            _pushCameraLink(srcView, dstViews)

    @exportRpc("viewport.view.link")
    def updateViewLink(self, viewId=None, linkState=False):
        if viewId:
            if linkState:
                self.linkedViews.append(viewId)
            else:
                try:
                    self.linkedViews.remove(viewId)
                except Exception:
                    pass
            # self.validateViewLinks()

        if len(self.linkedViews) > 1:
            allViews = [self.getView(vid) for vid in self.linkedViews]
            _pushCameraLink(allViews[0], allViews[1:])

        if self.onLinkChange:
            self.onLinkChange(self.linkedViews)

        if linkState:
            self.getApplication().InvokeEvent("UpdateEvent")

        return self.linkedViews

    # -------------------------------------------------------------------------
    # Mouse handling
    # -------------------------------------------------------------------------

    @exportRpc("viewport.mouse.interaction")
    def mouseInteraction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        if "x" not in event or "y" not in event:
            return 0

        view = self.getView(event["view"])

        if hasattr(view, "UseInteractiveRenderingForScreenshots"):
            if event["action"] == "down":
                view.UseInteractiveRenderingForScreenshots = 1
            elif event["action"] == "up":
                view.UseInteractiveRenderingForScreenshots = 0

        buttons = 0
        if event["buttonLeft"]:
            buttons |= vtkWebInteractionEvent.LEFT_BUTTON
        if event["buttonMiddle"]:
            buttons |= vtkWebInteractionEvent.MIDDLE_BUTTON
        if event["buttonRight"]:
            buttons |= vtkWebInteractionEvent.RIGHT_BUTTON

        modifiers = 0
        if event["shiftKey"]:
            modifiers |= vtkWebInteractionEvent.SHIFT_KEY
        if event["ctrlKey"]:
            modifiers |= vtkWebInteractionEvent.CTRL_KEY
        if event["altKey"]:
            modifiers |= vtkWebInteractionEvent.ALT_KEY
        if event["metaKey"]:
            modifiers |= vtkWebInteractionEvent.META_KEY

        pvevent = vtkWebInteractionEvent()
        pvevent.SetButtons(buttons)
        pvevent.SetModifiers(modifiers)
        pvevent.SetX(event["x"])
        pvevent.SetY(event["y"])
        # pvevent.SetKeyCode(event["charCode"])
        retVal = self.getApplication().HandleInteractionEvent(view.SMProxy, pvevent)
        del pvevent

        self.activeViewId = view.GetGlobalIDAsString()

        if event["action"] == "down" and self.lastAction != event["action"]:
            self.getApplication().InvokeEvent("StartInteractionEvent")

        if event["action"] == "up" and self.lastAction != event["action"]:
            self.getApplication().InvokeEvent("EndInteractionEvent")

        # if retVal :
        #  self.getApplication().InvokeEvent('UpdateEvent')

        if self.activeViewId in self.linkedViews:
            dstViews = [self.getView(vid) for vid in self.linkedViews]
            _pushCameraLink(view, dstViews)

        self.lastAction = event["action"]

        return retVal

    @exportRpc("viewport.mouse.zoom.wheel")
    def updateZoomFromWheel(self, event):
        if "Start" in event["type"]:
            self.getApplication().InvokeEvent("StartInteractionEvent")

        viewProxy = self.getView(event["view"])
        if viewProxy and "spinY" in event:
            rootId = viewProxy.GetGlobalIDAsString()
            zoomFactor = 1.0 - event["spinY"] / 10.0

            fp = viewProxy.CameraFocalPoint
            pos = viewProxy.CameraPosition
            delta = [fp[i] - pos[i] for i in range(3)]
            viewProxy.GetActiveCamera().Zoom(zoomFactor)
            viewProxy.UpdatePropertyInformation()
            pos2 = viewProxy.CameraPosition
            viewProxy.CameraFocalPoint = [pos2[i] + delta[i] for i in range(3)]

            if rootId in self.linkedViews:
                dstViews = [self.getView(vid) for vid in self.linkedViews]
                _pushCameraLink(viewProxy, dstViews)

        if "End" in event["type"]:
            self.getApplication().InvokeEvent("EndInteractionEvent")


CAMERA_PROP_NAMES = [
    "CameraFocalPoint",
    "CameraParallelProjection",
    "CameraParallelScale",
    "CameraPosition",
    "CameraViewAngle",
    "CameraViewUp",
]


def _pushCameraLink(viewSrc, viewDstList):
    props = {}
    for name in CAMERA_PROP_NAMES:
        props[name] = getattr(viewSrc, name)
    for v in viewDstList:
        for name in CAMERA_PROP_NAMES:
            v.__setattr__(name, props[name])
    return props
