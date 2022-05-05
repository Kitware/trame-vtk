class HybridView:
    def __init__(
        self,
        helper,
        view,
        namespace="view",
        mode="local",
        interactive_ratio=1,
        interactive_quality=60,
        still_ratio=1,
        still_quality=98,
    ):
        self._helper = helper
        self._app = helper._app
        self._view = view
        self._view_id = self._helper.id(view)

        # Image setup
        self.i_ratio = interactive_ratio
        self.i_quality = interactive_quality
        self.s_ratio = still_ratio
        self.s_quality = still_quality

        # init keys
        self.ref_key = namespace
        self.mode_key = f"{namespace}Mode" if namespace else "mode"
        self.scene_key = f"{namespace}Scene" if namespace else "scene"
        self.camera_key = f"{namespace}Camera" if namespace else "camera"
        self.animation_key = f"{namespace}Animate" if namespace else "animate"
        self.id_key = f"{namespace}Id" if namespace else "id"

        # Attach annotations
        self._app.state[self.id_key] = self._view_id
        self._app.state[self.mode_key] = mode
        self._app.trigger(self.camera_key)(self.update_camera)
        self._app.trigger(f"{self.animation_key}Start")(self.start_animation)
        self._app.trigger(f"{self.animation_key}Stop")(self.stop_animation)

    def replace_view(self, new_view):
        self._view = new_view
        self._view_id = self._helper.id(new_view)
        self._app.state[self.id_key] = self._view_id

    def start_animation(self):
        self._app.state[self.mode_key] = "remote"
        self._app.protocol_call(
            "viewport.image.push.quality", self._view_id, self.i_quality, self.i_ratio
        )
        self._app.protocol_call("viewport.image.animation.start", self._view_id)

    def stop_animation(self):
        self._app.protocol_call("viewport.image.animation.stop", self._view_id)
        self._app.protocol_call(
            "viewport.image.push.quality", self._view_id, self.s_quality, self.s_ratio
        )
        self.push_geometry()
        self._app.state[self.mode_key] = "local"

    def push_geometry(self):
        self._app.state[self.scene_key] = self._helper.scene(self._view)

    def push_image(self):
        self._helper.push_image(self._view)

    def update_camera(self, camera=None):
        if camera:
            self._helper.set_camera(self._view, **camera)
            self.push_image()
        else:
            # Need to update local camera
            camera = self._helper.camera(self._view)
            self._app.update(ref=self.ref_key, method="setCamera", args=[camera])
