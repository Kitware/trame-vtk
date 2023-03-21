from wslink.websocket import LinkProtocol


class vtkWebProtocol(LinkProtocol):
    """Base class for any VTK Web based protocol"""

    def getApplication(self):
        return self.getSharedObject("app")

    # no need for a setApplication anymore, but keep for compatibility
    def setApplication(self, app):
        pass

    def mapIdToObject(self, id):
        """
        Maps global-id for a vtkObject to the vtkObject instance. May return None if the
        id is not valid.
        """
        id = int(id)
        if id <= 0:
            return None
        return self.getApplication().GetObjectIdMap().GetVTKObject(id)

    def getGlobalId(self, obj):
        """
        Return the id for a given vtkObject
        """
        return self.getApplication().GetObjectIdMap().GetGlobalId(obj)

    def freeObject(self, obj):
        """
        Delete the given vtkObject from the objectIdMap. Returns true if delete succeeded.
        """
        return self.getApplication().GetObjectIdMap().FreeObject(obj)

    def freeObjectById(self, id):
        """
        Delete the vtkObject corresponding to the given objectId from the objectIdMap.
        Returns true if delete succeeded.
        """
        return self.getApplication().GetObjectIdMap().FreeObjectById(id)

    def getView(self, vid):
        """
        Returns the view for a given view ID, if vid is None then return the
        current active view.
        :param vid: The view ID
        :type vid: str
        """
        v = self.mapIdToObject(vid)

        if not v:
            # Use active view is none provided.
            v = self.getApplication().GetObjectIdMap().GetActiveObject("VIEW")
        if not v:
            raise Exception("no view provided: %s" % vid)

        return v

    def setActiveView(self, view):
        """
        Set a vtkRenderWindow to be the active one
        """
        self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", view)
