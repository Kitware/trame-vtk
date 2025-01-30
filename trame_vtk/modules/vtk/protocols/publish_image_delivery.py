import base64
import time

from wslink import register as export_rpc
from wslink import schedule_callback

from .web_protocol import vtkWebProtocol


class vtkWebPublishImageDelivery(vtkWebProtocol):
    """Provide publish-based Image delivery mechanism"""

    def __init__(self, decode=True):
        super().__init__()
        self.tracking_views = {}
        self.last_stale_time = {}
        self.stale_handler_count = {}
        self.delta_stale_time_before_render = 0.5  # 0.5s
        self.stale_count_limit = 10
        self.decode = decode
        self.views_in_animations = []
        self.target_frame_rate = 30.0
        self.min_frame_rate = 12.0
        self.max_frame_rate = 30.0

    def push_render(self, v_id, ignore_animation=False, stale_count=0):
        if v_id not in self.tracking_views:
            return

        if not self.tracking_views[v_id]["enabled"]:
            return

        if not ignore_animation and len(self.views_in_animations) > 0:
            return

        if "originalSize" not in self.tracking_views[v_id]:
            view = self.get_view(v_id)
            self.tracking_views[v_id]["originalSize"] = list(view.GetSize())

        if "ratio" not in self.tracking_views[v_id]:
            self.tracking_views[v_id]["ratio"] = 1

        ratio = self.tracking_views[v_id]["ratio"]
        mtime = self.tracking_views[v_id]["mtime"]
        quality = self.tracking_views[v_id]["quality"]
        size = [
            int((s * ratio) + 0.5) for s in self.tracking_views[v_id]["originalSize"]
        ]

        reply = self.still_render(
            {"view": v_id, "mtime": mtime, "quality": quality, "size": size}
        )
        stale = reply["stale"]
        if reply["image"]:
            # depending on whether the app has encoding enabled:
            if self.decode:
                reply["image"] = base64.standard_b64decode(reply["image"])

            reply["image"] = self.addAttachment(reply["image"])
            reply["format"] = "jpeg"
            # save mtime for next call.
            self.tracking_views[v_id]["mtime"] = reply["mtime"]
            # echo back real ID, instead of -1 for 'active'
            reply["id"] = v_id
            self.publish("viewport.image.push.subscription", reply)
        if stale:
            # The image has not been encoded yet.
            self.last_stale_time[v_id] = time.time()
            if self.stale_handler_count[v_id] == 0:
                self.stale_handler_count[v_id] += 1
                schedule_callback(
                    self.delta_stale_time_before_render,
                    lambda: self.render_stale_image(v_id, stale_count),
                )
        else:
            self.last_stale_time[v_id] = 0

    def render_stale_image(self, v_id, stale_count=0):
        if v_id in self.stale_handler_count and self.stale_handler_count[v_id] > 0:
            self.stale_handler_count[v_id] -= 1

            if self.last_stale_time[v_id] != 0:
                delta = time.time() - self.last_stale_time[v_id]
                # Break on stale_count otherwise linked view will always report to be stale
                # And loop forever
                if (
                    delta >= (self.delta_stale_time_before_render * (stale_count + 1))
                    and stale_count < self.stale_count_limit
                ):
                    self.push_render(v_id, False, stale_count + 1)
                elif delta < self.delta_stale_time_before_render:
                    self.stale_handler_count[v_id] += 1
                    schedule_callback(
                        self.delta_stale_time_before_render - delta + 0.001,
                        lambda: self.render_stale_image(v_id, stale_count),
                    )

    def animate(self):
        if len(self.views_in_animations) == 0:
            return

        next_animate_time = time.time() + 1.0 / self.target_frame_rate
        for v_id in self.views_in_animations:
            self.push_render(v_id, True)

        next_animate_time -= time.time()

        if self.target_frame_rate > self.max_frame_rate:
            self.target_frame_rate = self.max_frame_rate

        if next_animate_time < 0:
            if next_animate_time < -1.0:
                self.target_frame_rate = 1
            if self.target_frame_rate > self.min_frame_rate:
                self.target_frame_rate -= 1.0
            schedule_callback(0.001, lambda: self.animate())
        else:
            if (
                self.target_frame_rate < self.max_frame_rate
                and next_animate_time > 0.005
            ):
                self.target_frame_rate += 1.0
            schedule_callback(next_animate_time, lambda: self.animate())

    @export_rpc("viewport.image.animation.fps.max")
    def set_max_frame_rate(self, fps=30):
        self.max_frame_rate = fps

    @export_rpc("viewport.image.animation.fps.get")
    def get_current_frame_rate(self):
        return self.target_frame_rate

    @export_rpc("viewport.image.animation.start")
    def start_view_animation(self, view_id="-1"):
        s_view = self.get_view(view_id)
        real_view_id = str(self.get_global_id(s_view))

        self.views_in_animations.append(real_view_id)
        if len(self.views_in_animations) == 1:
            self.animate()

    @export_rpc("viewport.image.animation.stop")
    def stop_view_animation(self, view_id="-1"):
        s_view = self.get_view(view_id)
        real_view_id = str(self.get_global_id(s_view))

        if real_view_id in self.views_in_animations:
            self.views_in_animations.remove(real_view_id)

    @export_rpc("viewport.image.push")
    def image_push(self, options):
        s_view = self.get_view(options["view"])
        real_view_id = str(self.get_global_id(s_view))
        # Make sure an image is pushed
        self.app.InvalidateCache(s_view)
        self.push_render(real_view_id)

    # Internal function since the reply[image] is not
    # JSON(serializable) it can not be an RPC one
    def still_render(self, options):
        """
        RPC Callback to render a view and obtain the rendered image.
        """
        begin_time = int(round(time.time() * 1000))
        view = self.get_view(options["view"])
        if not view:
            # The view has been deleted, we can not render it...
            # Clean up old view state
            real_view_id = str(self.get_global_id(view))
            if real_view_id in self.views_in_animations:
                self.views_in_animations.remove(real_view_id)
            if real_view_id in self.tracking_views:
                del self.tracking_views[real_view_id]
            if real_view_id in self.stale_handler_count:
                del self.stale_handler_count[real_view_id]

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
        local_time = 0
        if options and "localTime" in options:
            local_time = options["localTime"]
        reply = {}
        app = self.app
        if t == 0:
            app.InvalidateCache(view)
        if self.decode:
            still_render = app.StillRenderToString
        else:
            still_render = app.StillRenderToBuffer
        reply_image = still_render(view, t, quality)

        # Check that we are getting image size we have set if not wait until we
        # do. The render call will set the actual window size.
        tries = 10
        while resize and list(view.GetSize()) != size and size != [0, 0] and tries > 0:
            app.InvalidateCache(view)
            reply_image = still_render(view, t, quality)
            tries -= 1

        if (
            not resize
            and options
            and ("clearCache" in options)
            and options["clearCache"]
        ):
            app.InvalidateCache(view)
            reply_image = still_render(view, t, quality)

        reply["stale"] = app.GetHasImagesBeingProcessed(view)
        reply["mtime"] = app.GetLastStillRenderToMTime()
        reply["size"] = view.GetSize()[0:2]
        reply["memsize"] = reply_image.GetDataSize() if reply_image else 0
        reply["format"] = "jpeg;base64" if self.decode else "jpeg"
        reply["global_id"] = str(self.get_global_id(view))
        reply["localTime"] = local_time
        if self.decode:
            reply["image"] = reply_image
        else:
            # Convert the vtkUnsignedCharArray into a bytes object, required by Autobahn websockets
            reply["image"] = memoryview(reply_image).tobytes() if reply_image else None

        end_time = int(round(time.time() * 1000))
        reply["workTime"] = end_time - begin_time

        return reply

    @export_rpc("viewport.image.push.observer.add")
    def add_render_observer(self, view_id):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = str(self.get_global_id(s_view))

        if real_view_id not in self.tracking_views:

            def observer_callback(*_, **__):
                return self.push_render(real_view_id)

            def start_callback(*_, **__):
                return self.start_view_animation(real_view_id)

            def stop_callback(*_, **__):
                return self.stop_view_animation(real_view_id)

            tag = self.app.AddObserver("UpdateEvent", observer_callback)
            tag_start = self.app.AddObserver("StartInteractionEvent", start_callback)
            tag_stop = self.app.AddObserver("EndInteractionEvent", stop_callback)
            # TODO do we need self.app.AddObserver('ResetActiveView', reset_active_view())
            self.tracking_views[real_view_id] = {
                "tags": [tag, tag_start, tag_stop],
                "observerCount": 1,
                "mtime": 0,
                "enabled": True,
                "quality": 100,
            }
            self.stale_handler_count[real_view_id] = 0
        else:
            # There is an observer on this view already
            self.tracking_views[real_view_id]["observerCount"] += 1

        self.push_render(real_view_id)
        return {"success": True, "viewId": real_view_id}

    @export_rpc("viewport.image.push.observer.remove")
    def remove_render_observer(self, view_id):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = str(self.get_global_id(s_view))

        observer_info = None
        if real_view_id in self.tracking_views:
            observer_info = self.tracking_views[real_view_id]

        if not observer_info:
            return {"error": "Unable to find subscription for view %s" % real_view_id}

        observer_info["observerCount"] -= 1

        if observer_info["observerCount"] <= 0:
            for tag in observer_info["tags"]:
                self.app.RemoveObserver(tag)
            del self.tracking_views[real_view_id]

        return {"result": "success"}

    @export_rpc("viewport.image.push.quality.get")
    def get_view_quality(self, view_id):
        response = dict(quality=1, ratio=1)
        s_view = self.get_view(view_id)

        if s_view:
            real_view_id = str(self.get_global_id(s_view))
            if real_view_id in self.tracking_views:
                observer_info = self.tracking_views[real_view_id]
                response["quality"] = observer_info.get("quality", 100)
                response["ratio"] = observer_info.get("ratio", 1)

        return response

    @export_rpc("viewport.image.push.quality")
    def set_view_quality(self, view_id, quality, ratio=1):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = str(self.get_global_id(s_view))
        observer_info = None
        if real_view_id in self.tracking_views:
            observer_info = self.tracking_views[real_view_id]

        if not observer_info:
            return {"error": "Unable to find subscription for view %s" % real_view_id}

        observer_info["quality"] = quality
        observer_info["ratio"] = ratio

        # Update image size right now!
        if "originalSize" in self.tracking_views[real_view_id]:
            size = [
                int((s * ratio) + 0.5)
                for s in self.tracking_views[real_view_id]["originalSize"]
            ]
            if hasattr(s_view, "SetSize"):
                s_view.SetSize(size)
            else:
                s_view.ViewSize = size

        return {"result": "success"}

    @export_rpc("viewport.image.push.original.size")
    def set_view_size(self, view_id, width, height):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = str(self.get_global_id(s_view))
        observer_info = None
        if real_view_id in self.tracking_views:
            observer_info = self.tracking_views[real_view_id]

        if not observer_info:
            return {"error": "Unable to find subscription for view %s" % real_view_id}

        observer_info["originalSize"] = [width, height]

        return {"result": "success"}

    @export_rpc("viewport.image.push.enabled")
    def enable_view(self, view_id, enabled):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = str(self.get_global_id(s_view))
        observer_info = None
        if real_view_id in self.tracking_views:
            observer_info = self.tracking_views[real_view_id]

        if not observer_info:
            return {"error": "Unable to find subscription for view %s" % real_view_id}

        observer_info["enabled"] = enabled

        return {"result": "success"}

    @export_rpc("viewport.image.push.invalidate.cache")
    def invalidate_cache(self, view_id):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        self.app.InvalidateCache(s_view)
        self.app.InvokeEvent("UpdateEvent")
        return {"result": "success"}
