import base64
import math
import time

from paraview import simple
from wslink import register as export_rpc
from wslink import schedule_callback

from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from .web_protocol import ParaViewWebProtocol


def apply_modifiers(event, interactor):
    interactor.SetShiftKey(1 if event.get("shiftKey") else 0)
    interactor.SetControlKey(1 if event.get("ctrlKey") else 0)
    interactor.SetAltKey(1 if event.get("altKey") else 0)
    # interactor.SetMetaKey(1 if event.get("metaKey") else 0)


class ParaViewWebPublishImageDelivery(ParaViewWebProtocol):
    def __init__(self, decode=True, **kwargs):
        super().__init__()
        self.tracking_views = {}
        self.last_stale_time = {}
        self.stale_handler_count = {}
        self.delta_stale_time_before_render = 0.1  # 0.1s
        self.stale_count_limit = 10
        self.decode = decode
        self.views_in_animations = []
        self.target_frame_rate = 30.0
        self.min_frame_rate = 12.0
        self.max_frame_rate = 30.0

        # Camera link handling
        self.linked_views = []
        self.link_names = []
        self.on_link_change = None

        # Mouse handling
        self.last_action = "up"
        self.active_view_id = None

    # In case some external protocol wants to monitor when link views change
    def set_link_change_callback(self, fn):
        self.on_link_change = fn

    def push_render(self, v_id, ignore_animation=False, stale_count=0):
        if v_id not in self.tracking_views:
            return

        if not self.tracking_views[v_id]["enabled"]:
            return

        if not ignore_animation and len(self.views_in_animations) > 0:
            return

        if "originalSize" not in self.tracking_views[v_id]:
            view = self.get_view(v_id)
            self.tracking_views[v_id]["originalSize"] = (
                int(view.ViewSize[0] + 0.5),
                int(view.ViewSize[1] + 0.5),
            )

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
            self.tracking_views[v_id]["mtime"] = reply["mtime"]
            # echo back real ID, instead of -1 for 'active'
            reply["id"] = v_id
            self.publish("viewport.image.push.subscription", reply)
        if stale:
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

    def animate(self, render_all_views=True):
        if len(self.views_in_animations) == 0:
            return

        next_animate_time = time.time() + 1.0 / self.target_frame_rate

        # Handle the rendering of the views
        if self.active_view_id:
            self.push_render(self.active_view_id, True)

        if render_all_views:
            for v_id in set(self.views_in_animations):
                if v_id != self.active_view_id:
                    self.push_render(v_id, True)

        next_animate_time -= time.time()

        if self.target_frame_rate > self.max_frame_rate:
            self.target_frame_rate = self.max_frame_rate

        if next_animate_time < 0:
            if next_animate_time < -1.0:
                self.target_frame_rate = 1
            if self.target_frame_rate > self.min_frame_rate:
                self.target_frame_rate -= 1.0
            if self.active_view_id:
                # If active view, prioritize that one over the others
                # -> Divide by 2 the refresh rate of the other views
                schedule_callback(0.001, lambda: self.animate(not render_all_views))
            else:
                # Keep animating at the best rate we can
                schedule_callback(0.001, lambda: self.animate())
        else:
            # We have time so let's render all
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
        real_view_id = s_view.GetGlobalIDAsString()

        self.views_in_animations.append(real_view_id)
        if len(self.views_in_animations) == 1:
            self.animate()

    @export_rpc("viewport.image.animation.stop")
    def stop_view_animation(self, view_id="-1"):
        s_view = self.get_view(view_id)
        real_view_id = s_view.GetGlobalIDAsString()

        if (
            real_view_id in self.views_in_animations
            and real_view_id in self.tracking_views
        ):
            progress_rendering = self.tracking_views[real_view_id]["streaming"]
            self.views_in_animations.remove(real_view_id)
            if progress_rendering:
                self.progressive_render(real_view_id)

    def progressive_render(self, view_id="-1"):
        s_view = self.get_view(view_id)
        real_view_id = s_view.GetGlobalIDAsString()

        if real_view_id in self.views_in_animations:
            return

        if s_view.GetSession().GetPendingProgress():
            schedule_callback(
                self.delta_stale_time_before_render,
                lambda: self.progressive_render(view_id),
            )
        else:
            again = s_view.StreamingUpdate(True)
            self.push_render(real_view_id, True)

            if again:
                schedule_callback(0.001, lambda: self.progressive_render(view_id))

    @export_rpc("viewport.image.push")
    def image_push(self, options):
        view = self.get_view(options["view"])
        view_id = view.GetGlobalIDAsString()

        # Make sure an image is pushed
        self.app.InvalidateCache(view.SMProxy)

        self.push_render(view_id)

    # Internal function since the reply[image] is not
    # JSON(serializable) it can not be an RPC one
    def still_render(self, options):
        """
        RPC Callback to render a view and obtain the rendered image.
        """
        begin_time = int(round(time.time() * 1000))
        view_id = str(options["view"])
        view = self.get_view(view_id)

        # If no view id provided, skip rendering
        if not view_id:
            print("No view")
            print(options)
            return None

        # Make sure request match our selected view
        if view_id != "-1" and view.GetGlobalIDAsString() != view_id:
            # We got active view rather than our request
            view = None

        # No view to render => need some cleanup
        if not view:
            # The view has been deleted, we can not render it...
            # Clean up old view state
            if view_id in self.views_in_animations:
                self.views_in_animations.remove(view_id)

            if view_id in self.tracking_views:
                del self.tracking_views[view_id]

            if view_id in self.stale_handler_count:
                del self.stale_handler_count[view_id]

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
        local_time = 0
        if options and "localTime" in options:
            local_time = options["localTime"]
        reply = {}
        app = self.app
        if t == 0:
            app.InvalidateCache(view.SMProxy)
        if self.decode:
            still_render = app.StillRenderToString
        else:
            still_render = app.StillRenderToBuffer
        reply_image = still_render(view.SMProxy, t, quality)

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
            reply_image = still_render(view.SMProxy, t, quality)
            tries -= 1

        if (
            not resize
            and options
            and ("clearCache" in options)
            and options["clearCache"]
        ):
            app.InvalidateCache(view.SMProxy)
            reply_image = still_render(view.SMProxy, t, quality)

        # Pack the result
        reply["stale"] = app.GetHasImagesBeingProcessed(view.SMProxy)
        reply["mtime"] = app.GetLastStillRenderToMTime()
        reply["size"] = view.ViewSize[0:2]
        reply["memsize"] = reply_image.GetDataSize() if reply_image else 0
        reply["format"] = "jpeg;base64" if self.decode else "jpeg"
        reply["global_id"] = view.GetGlobalIDAsString()
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

        real_view_id = s_view.GetGlobalIDAsString()

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
                "streaming": s_view.GetClientSideObject().GetEnableStreaming(),
            }
            self.stale_handler_count[real_view_id] = 0
        else:
            # There is an observer on this view already
            self.tracking_views[real_view_id]["observerCount"] += 1

        self.push_render(real_view_id)
        return {"success": True, "viewId": real_view_id}

    @export_rpc("viewport.image.push.observer.remove")
    def remove_render_observer(self, view_id):
        s_view = None
        try:
            s_view = self.get_view(view_id)
        except Exception:
            print("no view with ID %s available in remove_render_observer" % view_id)

        real_view_id = s_view.GetGlobalIDAsString() if s_view else view_id

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
            del self.stale_handler_count[real_view_id]

        return {"result": "success"}

    @export_rpc("viewport.image.push.quality.get")
    def get_view_quality(self, view_id):
        response = dict(quality=1, ratio=1)
        s_view = self.get_view(view_id)

        if s_view:
            real_view_id = s_view.GetGlobalIDAsString()
            if real_view_id in self.tracking_views:
                observer_info = self.tracking_views[real_view_id]
                response["quality"] = observer_info.get("quality", 100)
                response["ratio"] = observer_info.get("ratio", 1)

        return response

    @export_rpc("viewport.image.push.quality")
    def set_view_quality(self, view_id, quality, ratio=1, update_linked_view=True):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = s_view.GetGlobalIDAsString()
        observer_info = None
        if real_view_id in self.tracking_views:
            observer_info = self.tracking_views[real_view_id]

        if not observer_info:
            return {"error": "Unable to find subscription for view %s" % real_view_id}

        observer_info["quality"] = quality
        observer_info["ratio"] = ratio

        # Handle linked view quality/ratio synch
        if update_linked_view and real_view_id in self.linked_views:
            for vid in self.linked_views:
                self.set_view_quality(vid, quality, ratio, False)

        # Update image size right now!
        if "originalSize" in self.tracking_views[real_view_id]:
            size = [
                int((s * ratio) + 0.5)
                for s in self.tracking_views[real_view_id]["originalSize"]
            ]
            if "SetSize" in s_view:
                s_view.SetSize(size)
            else:
                s_view.ViewSize = size

        return {"result": "success"}

    @export_rpc("viewport.image.push.original.size")
    def set_view_size(self, view_id, width, height):
        if width < 10 or height < 10:
            return {"result": "size skip"}

        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = s_view.GetGlobalIDAsString()
        observer_info = None
        if real_view_id in self.tracking_views:
            observer_info = self.tracking_views[real_view_id]

        if not observer_info:
            return {"error": "Unable to find subscription for view %s" % real_view_id}

        observer_info["originalSize"] = (int(width + 0.5), int(height + 0.5))

        return {"result": "success"}

    @export_rpc("viewport.image.push.enabled")
    def enable_view(self, view_id, enabled):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = s_view.GetGlobalIDAsString()
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

        self.app.InvalidateCache(s_view.SMProxy)
        self.app.InvokeEvent("UpdateEvent")
        return {"result": "success"}

    # -------------------------------------------------------------------------
    # View linked
    # -------------------------------------------------------------------------

    def validate_view_links(self):
        for link_name in self.link_names:
            simple.RemoveCameraLink(link_name)
        self.link_names = []

        if len(self.linked_views) > 1:
            view_list = [self.get_view(vid) for vid in self.linked_views]
            ref_view = view_list.pop(0)
            for view in view_list:
                link_name = "%s_%s" % (
                    ref_view.GetGlobalIDAsString(),
                    view.GetGlobalIDAsString(),
                )
                simple.AddCameraLink(ref_view, view, link_name)
                self.link_names.append(link_name)

            # Synch camera state
            src_view = view_list[0]
            dst_views = view_list[1:]
            _push_camera_link(src_view, dst_views)

    @export_rpc("viewport.view.link")
    def update_view_link(self, view_id=None, link_state=False):
        if view_id:
            if link_state:
                self.linked_views.append(view_id)
            else:
                try:
                    self.linked_views.remove(view_id)
                except Exception:
                    pass
            # self.validate_view_links()

        if len(self.linked_views) > 1:
            all_views = [self.get_view(vid) for vid in self.linked_views]
            _push_camera_link(all_views[0], all_views[1:])

        if self.on_link_change:
            self.on_link_change(self.linked_views)

        if link_state:
            self.app.InvokeEvent("UpdateEvent")

        return self.linked_views

    # -------------------------------------------------------------------------
    # Mouse handling
    # -------------------------------------------------------------------------

    @export_rpc("viewport.mouse.interaction")
    def mouse_interaction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        if "x" not in event or "y" not in event:
            return 0

        view = self.get_view(event["view"])

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
        ret_val = self.app.HandleInteractionEvent(view.SMProxy, pvevent)
        del pvevent

        self.active_view_id = view.GetGlobalIDAsString()

        if event["action"] == "down" and self.last_action != event["action"]:
            self.app.InvokeEvent("StartInteractionEvent")

        if event["action"] == "up" and self.last_action != event["action"]:
            self.app.InvokeEvent("EndInteractionEvent")

        # if ret_val :
        #  self.app.InvokeEvent('UpdateEvent')

        if self.active_view_id in self.linked_views:
            dst_views = [self.get_view(vid) for vid in self.linked_views]
            _push_camera_link(view, dst_views)

        self.last_action = event["action"]

        return ret_val

    @export_rpc("viewport.mouse.zoom.wheel")
    def update_zoom_from_wheel(self, event):
        view_proxy = self.get_view(event["view"])

        if not view_proxy:
            return

        interactor = view_proxy.GetInteractor()
        if not interactor:
            # Can't do anything.
            return

        apply_modifiers(event, interactor)

        if "x" in event and "y" in event and interactor.GetRenderWindow():
            # Set the mouse position, so that if there are multiple
            # renderers, the interactor can figure out which one should
            # be modified.
            view_size = interactor.GetRenderWindow().GetSize()
            pos_x = math.floor(view_size[0] * event["x"] + 0.5)
            pos_y = math.floor(view_size[1] * event["y"] + 0.5)

            interactor.SetEventPosition(pos_x, pos_y)
            interactor.MouseMoveEvent()

        if "Start" in event["type"]:
            self.app.InvokeEvent("StartInteractionEvent")
            # It seems every time a StartInteractionEvent is sent, a
            # mouse wheel event with the same spin is sent afterward. We
            # don't want to zoom twice, so do not perform a zoom on the
            # StartInteractionEvent.
            return

        if "End" in event["type"]:
            self.app.InvokeEvent("EndInteractionEvent")
            # This is done
            return

        spin_y = event.get("spinY", 0)
        direction = "Backward" if spin_y >= 0 else "Forward"
        method = getattr(interactor, f"MouseWheel{direction}Event")

        style = interactor.GetInteractorStyle()
        prev_motion_factor = style.GetMouseWheelMotionFactor()
        style.SetMouseWheelMotionFactor(prev_motion_factor * abs(spin_y))
        try:
            method()
        finally:
            style.SetMouseWheelMotionFactor(prev_motion_factor)

        view_proxy.UpdatePropertyInformation()

        root_id = view_proxy.GetGlobalIDAsString()
        if root_id in self.linked_views:
            dst_views = [self.get_view(vid) for vid in self.linked_views]
            _push_camera_link(view_proxy, dst_views)


CAMERA_PROP_NAMES = [
    "CameraFocalPoint",
    "CameraParallelProjection",
    "CameraParallelScale",
    "CameraPosition",
    "CameraViewAngle",
    "CameraViewUp",
]


def _push_camera_link(view_src, view_dst_list):
    props = {}
    for name in CAMERA_PROP_NAMES:
        props[name] = getattr(view_src, name)
    for v in view_dst_list:
        for name in CAMERA_PROP_NAMES:
            v.__setattr__(name, props[name])
    return props
