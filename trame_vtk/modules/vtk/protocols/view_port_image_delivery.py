import time

from wslink import register as exportRpc

from .web_protocol import vtkWebProtocol


class vtkWebViewPortImageDelivery(vtkWebProtocol):
    """Provide Image delivery mechanism (deprecated - will be removed in VTK 10+)"""

    @exportRpc("viewport.image.render")
    def stillRender(self, options):
        """
        RPC Callback to render a view and obtain the rendered image.
        """
        beginTime = int(round(time.time() * 1000))
        view = self.getView(options["view"])
        size = [view.GetSize()[0], view.GetSize()[1]]
        # use existing size, overridden only if options["size"] is set.
        resize = size != options.get("size", size)
        if resize:
            size = options["size"]
            if size[0] > 0 and size[1] > 0:
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
        reply["image"] = app.StillRenderToString(view, t, quality)
        # Check that we are getting image size we have set. If not, wait until we
        # do. The render call will set the actual window size.
        tries = 10
        while resize and list(view.GetSize()) != size and size != [0, 0] and tries > 0:
            app.InvalidateCache(view)
            reply["image"] = app.StillRenderToString(view, t, quality)
            tries -= 1

        reply["stale"] = app.GetHasImagesBeingProcessed(view)
        reply["mtime"] = app.GetLastStillRenderToMTime()
        reply["size"] = [view.GetSize()[0], view.GetSize()[1]]
        reply["format"] = "jpeg;base64"
        reply["global_id"] = str(self.getGlobalId(view))
        reply["localTime"] = localTime

        endTime = int(round(time.time() * 1000))
        reply["workTime"] = endTime - beginTime

        return reply
