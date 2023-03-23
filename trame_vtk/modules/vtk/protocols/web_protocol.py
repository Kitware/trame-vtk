from wslink.websocket import LinkProtocol


class vtkWebProtocol(LinkProtocol):
    """Base class for any VTK Web based protocol"""

    @property
    def app(self):
        return self.getSharedObject("app")

    def map_id_to_object(self, id):
        """
        Maps global-id for a vtkObject to the vtkObject instance. May return None if the
        id is not valid.
        """
        id = int(id)
        if id <= 0:
            return None
        return self.app.GetObjectIdMap().GetVTKObject(id)

    def get_global_id(self, obj):
        """
        Return the id for a given vtkObject
        """
        return self.app.GetObjectIdMap().GetGlobalId(obj)

    def free_object(self, obj):
        """
        Delete the given vtkObject from the object_id_map. Returns true if delete succeeded.
        """
        return self.app.GetObjectIdMap().FreeObject(obj)

    def free_object_by_id(self, id):
        """
        Delete the vtkObject corresponding to the given object_id from the object_id_map.
        Returns true if delete succeeded.
        """
        return self.app.GetObjectIdMap().FreeObjectById(id)

    def get_view(self, vid):
        """
        Returns the view for a given view ID, if vid is None then return the
        current active view.
        :param vid: The view ID
        :type vid: str
        """
        v = self.map_id_to_object(vid)

        if not v:
            # Use active view is none provided.
            v = self.app.GetObjectIdMap().GetActiveObject("VIEW")
        if not v:
            raise Exception("no view provided: %s" % vid)

        return v

    def set_active_view(self, view):
        """
        Set a vtkRenderWindow to be the active one
        """
        self.app.GetObjectIdMap().SetActiveObject("VIEW", view)
