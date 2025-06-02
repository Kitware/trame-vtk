from wslink import register as export_rpc

from ..serializers import (
    reference_id,
    initialize_serializers,
    serialize,
    serialize_widget,
    extract_array_hash,
    SynchronizationContext,
)
from .web_protocol import vtkWebProtocol


class vtkWebLocalRendering(vtkWebProtocol):
    """Improved geometry delivery for client-side rendering

    Provide an updated geometry delivery mechanism which better matches the
    client-side rendering capability we have in vtk.js
    """

    def __init__(self, **kwargs):
        super().__init__()
        initialize_serializers()
        self.context = SynchronizationContext()
        self.tracking_views = {}
        self.mtime = 0

    # RpcName: get_array => viewport.geometry.array.get
    @export_rpc("viewport.geometry.array.get")
    def get_array(self, data_hash, binary=False):
        if binary:
            return self.addAttachment(
                self.context.get_cached_data_array(data_hash, binary)
            )
        return self.context.get_cached_data_array(data_hash, binary)

    # RpcName: add_view_observer => viewport.geometry.view.observer.add
    @export_rpc("viewport.geometry.view.observer.add")
    def add_view_observer(self, view_id):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = self.app.GetObjectIdMap().GetGlobalId(s_view)

        def push_geometry(new_subscription=False):
            state_to_return = self.get_view_state(real_view_id, new_subscription)
            state_to_return["mtime"] = 0 if new_subscription else self.mtime
            self.mtime += 1
            return state_to_return

        if real_view_id not in self.tracking_views:

            def observer_callback(*_, **__):
                return self.publish(
                    "viewport.geometry.view.subscription",
                    push_geometry(),
                )

            tag = self.app.AddObserver("UpdateEvent", observer_callback)
            self.tracking_views[real_view_id] = {"tags": [tag], "observerCount": 1}
        else:
            # There is an observer on this view already
            self.tracking_views[real_view_id]["observerCount"] += 1

        self.publish("viewport.geometry.view.subscription", push_geometry(True))
        return {"success": True, "viewId": real_view_id}

    # RpcName: remove_view_observer => viewport.geometry.view.observer.remove
    @export_rpc("viewport.geometry.view.observer.remove")
    def remove_view_observer(self, view_id):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        real_view_id = self.app.GetObjectIdMap().GetGlobalId(s_view)

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

    # RpcName: get_view_state => viewport.geometry.view.get.state
    @export_rpc("viewport.geometry.view.get.state")
    def get_view_state(
        self,
        view_id,
        new_subscription=False,
        widgets=None,
        orientation_axis=0,
        **kwargs,
    ):
        s_view = self.get_view(view_id)
        if not s_view:
            return {"error": "Unable to get view with id %s" % view_id}

        self.context.set_ignore_last_dependencies(new_subscription)

        # Get the active view and render window, use it to iterate over renderers
        render_window = s_view
        renderer = render_window.GetRenderers().GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        render_window_id = self.app.GetObjectIdMap().GetGlobalId(s_view)
        view_instance = serialize(
            None, render_window, render_window_id, self.context, 1
        )
        view_instance["extra"] = {
            "vtkRefId": reference_id(render_window),
            "centerOfRotation": camera.GetFocalPoint(),
            "camera": reference_id(camera),
        }

        # Handle widgets/behaviors
        if widgets:
            behaviors = {}
            view_instance["behaviors"] = behaviors
            for widget in widgets:
                serialize_widget(behaviors, widget)
        elif orientation_axis:
            view_instance["behaviors"] = {
                "autoOrientation": 1,
            }

        self.context.set_ignore_last_dependencies(False)
        self.context.check_for_arrays_to_release()

        if view_instance:
            return view_instance

        return None

    @export_rpc("viewport.geometry.view.get.export")
    def get_standalone_state(self, view_id, widgets=None, orientation_axis=0, **kwargs):
        scene_description = self.get_view_state(
            view_id,
            new_subscription=True,
            widgets=widgets,
            orientation_axis=orientation_axis,
            **kwargs,
        )
        hashes = {}
        for entry in extract_array_hash(scene_description):
            data_hash = entry.get("hash")
            hashes[data_hash] = dict(
                **entry, content=self.context.get_cached_data_array(data_hash, False)
            )

        return dict(hashes=hashes, scene=scene_description)
