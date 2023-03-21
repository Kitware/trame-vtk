import base64
import time

from wslink import register as exportRpc
from wslink import schedule_callback

from .web_protocol import vtkWebProtocol


class vtkWebPublishImageDelivery(vtkWebProtocol):
    """Provide publish-based Image delivery mechanism"""

    def __init__(self, decode=True):
        super(vtkWebPublishImageDelivery, self).__init__()
        self.trackingViews = {}
        self.lastStaleTime = 0
        self.staleHandlerCount = 0
        self.deltaStaleTimeBeforeRender = 0.5  # 0.5s
        self.decode = decode
        self.viewsInAnimations = []
        self.targetFrameRate = 30.0
        self.minFrameRate = 12.0
        self.maxFrameRate = 30.0

    def pushRender(self, vId, ignoreAnimation=False):
        if vId not in self.trackingViews:
            return

        if not self.trackingViews[vId]["enabled"]:
            return

        if not ignoreAnimation and len(self.viewsInAnimations) > 0:
            return

        if "originalSize" not in self.trackingViews[vId]:
            view = self.getView(vId)
            self.trackingViews[vId]["originalSize"] = list(view.GetSize())

        if "ratio" not in self.trackingViews[vId]:
            self.trackingViews[vId]["ratio"] = 1

        ratio = self.trackingViews[vId]["ratio"]
        mtime = self.trackingViews[vId]["mtime"]
        quality = self.trackingViews[vId]["quality"]
        size = [int(s * ratio) for s in self.trackingViews[vId]["originalSize"]]

        reply = self.stillRender(
            {"view": vId, "mtime": mtime, "quality": quality, "size": size}
        )
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
            self.lastStaleTime = time.time()
            if self.staleHandlerCount == 0:
                self.staleHandlerCount += 1
                schedule_callback(
                    self.deltaStaleTimeBeforeRender, lambda: self.renderStaleImage(vId)
                )
        else:
            self.lastStaleTime = 0

    def renderStaleImage(self, vId):
        self.staleHandlerCount -= 1

        if self.lastStaleTime != 0:
            delta = time.time() - self.lastStaleTime
            if delta >= self.deltaStaleTimeBeforeRender:
                self.pushRender(vId)
            else:
                self.staleHandlerCount += 1
                schedule_callback(
                    self.deltaStaleTimeBeforeRender - delta + 0.001,
                    lambda: self.renderStaleImage(vId),
                )

    def animate(self):
        if len(self.viewsInAnimations) == 0:
            return

        nextAnimateTime = time.time() + 1.0 / self.targetFrameRate
        for vId in self.viewsInAnimations:
            self.pushRender(vId, True)

        nextAnimateTime -= time.time()

        if self.targetFrameRate > self.maxFrameRate:
            self.targetFrameRate = self.maxFrameRate

        if nextAnimateTime < 0:
            if nextAnimateTime < -1.0:
                self.targetFrameRate = 1
            if self.targetFrameRate > self.minFrameRate:
                self.targetFrameRate -= 1.0
            schedule_callback(0.001, lambda: self.animate())
        else:
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
        realViewId = str(self.getGlobalId(sView))

        self.viewsInAnimations.append(realViewId)
        if len(self.viewsInAnimations) == 1:
            self.animate()

    @exportRpc("viewport.image.animation.stop")
    def stopViewAnimation(self, viewId="-1"):
        sView = self.getView(viewId)
        realViewId = str(self.getGlobalId(sView))

        if realViewId in self.viewsInAnimations:
            self.viewsInAnimations.remove(realViewId)

    @exportRpc("viewport.image.push")
    def imagePush(self, options):
        sView = self.getView(options["view"])
        realViewId = str(self.getGlobalId(sView))
        # Make sure an image is pushed
        self.getApplication().InvalidateCache(sView)
        self.pushRender(realViewId)

    # Internal function since the reply[image] is not
    # JSON(serializable) it can not be an RPC one
    def stillRender(self, options):
        """
        RPC Callback to render a view and obtain the rendered image.
        """
        beginTime = int(round(time.time() * 1000))
        view = self.getView(options["view"])
        size = view.GetSize()[0:2]
        resize = size != options.get("size", size)
        if resize:
            size = options["size"]
            if size[0] > 10 and size[1] > 10:
                view.SetSize(size)
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
            app.InvalidateCache(view)
        if self.decode:
            stillRender = app.StillRenderToString
        else:
            stillRender = app.StillRenderToBuffer
        reply_image = stillRender(view, t, quality)

        # Check that we are getting image size we have set if not wait until we
        # do. The render call will set the actual window size.
        tries = 10
        while resize and list(view.GetSize()) != size and size != [0, 0] and tries > 0:
            app.InvalidateCache(view)
            reply_image = stillRender(view, t, quality)
            tries -= 1

        if (
            not resize
            and options
            and ("clearCache" in options)
            and options["clearCache"]
        ):
            app.InvalidateCache(view)
            reply_image = stillRender(view, t, quality)

        reply["stale"] = app.GetHasImagesBeingProcessed(view)
        reply["mtime"] = app.GetLastStillRenderToMTime()
        reply["size"] = view.GetSize()[0:2]
        reply["memsize"] = reply_image.GetDataSize() if reply_image else 0
        reply["format"] = "jpeg;base64" if self.decode else "jpeg"
        reply["global_id"] = str(self.getGlobalId(view))
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

        realViewId = str(self.getGlobalId(sView))

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
            }
        else:
            # There is an observer on this view already
            self.trackingViews[realViewId]["observerCount"] += 1

        self.pushRender(realViewId)
        return {"success": True, "viewId": realViewId}

    @exportRpc("viewport.image.push.observer.remove")
    def removeRenderObserver(self, viewId):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = str(self.getGlobalId(sView))

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

    @exportRpc("viewport.image.push.quality")
    def setViewQuality(self, viewId, quality, ratio=1):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = str(self.getGlobalId(sView))
        observerInfo = None
        if realViewId in self.trackingViews:
            observerInfo = self.trackingViews[realViewId]

        if not observerInfo:
            return {"error": "Unable to find subscription for view %s" % realViewId}

        observerInfo["quality"] = quality
        observerInfo["ratio"] = ratio

        # Update image size right now!
        if "originalSize" in self.trackingViews[realViewId]:
            size = [
                int(s * ratio) for s in self.trackingViews[realViewId]["originalSize"]
            ]
            if hasattr(sView, "SetSize"):
                sView.SetSize(size)
            else:
                sView.ViewSize = size

        return {"result": "success"}

    @exportRpc("viewport.image.push.original.size")
    def setViewSize(self, viewId, width, height):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = str(self.getGlobalId(sView))
        observerInfo = None
        if realViewId in self.trackingViews:
            observerInfo = self.trackingViews[realViewId]

        if not observerInfo:
            return {"error": "Unable to find subscription for view %s" % realViewId}

        observerInfo["originalSize"] = [width, height]

        return {"result": "success"}

    @exportRpc("viewport.image.push.enabled")
    def enableView(self, viewId, enabled):
        sView = self.getView(viewId)
        if not sView:
            return {"error": "Unable to get view with id %s" % viewId}

        realViewId = str(self.getGlobalId(sView))
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

        self.getApplication().InvalidateCache(sView)
        self.getApplication().InvokeEvent("UpdateEvent")
        return {"result": "success"}
