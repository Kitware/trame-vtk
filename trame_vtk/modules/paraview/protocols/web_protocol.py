import os

from paraview import simple
from paraview.servermanager import vtkSMTransferFunctionManager

from trame_vtk.modules.vtk.protocols.web_protocol import vtkWebProtocol


class ParaViewWebProtocol(vtkWebProtocol):
    def __init__(self):
        # self.Application = None
        self.coreServer = None
        self.multiRoot = False
        self.baseDirectory = ""
        self.baseDirectoryMap = {}

    def mapIdToProxy(self, id):
        """
        Maps global-id for a proxy to the proxy instance. May return None if the
        id is not valid.
        """
        try:
            id = int(id)
        except ValueError:
            return None
        if id <= 0:
            return None
        return simple.servermanager._getPyProxy(
            simple.servermanager.ActiveConnection.Session.GetRemoteObject(id)
        )

    def getView(self, vid):
        """
        Returns the view for a given view ID, if vid is None then return the
        current active view.
        :param vid: The view ID
        :type vid: str
        """
        view = self.mapIdToProxy(vid)
        if not view:
            # Use active view is none provided.
            view = simple.GetActiveView()

        if not view:
            raise Exception("no view provided: " + str(vid))

        return view

    def debug(self, msg):
        if self.debugMode:
            print(msg)

    def setBaseDirectory(self, basePath):
        self.overrideDataDirKey = None
        self.baseDirectory = ""
        self.baseDirectoryMap = {}
        self.multiRoot = False

        if basePath.find("|") < 0:
            if basePath.find("=") >= 0:
                basePair = basePath.split("=")
                if os.path.exists(basePair[1]):
                    self.baseDirectory = basePair[1]
                    self.overrideDataDirKey = basePair[0]
            else:
                self.baseDirectory = basePath
            self.baseDirectory = os.path.normpath(self.baseDirectory)
        else:
            baseDirs = basePath.split("|")
            for baseDir in baseDirs:
                basePair = baseDir.split("=")
                if os.path.exists(basePair[1]):
                    self.baseDirectoryMap[basePair[0]] = os.path.normpath(basePair[1])

            # Check if we ended up with just a single directory
            bdKeys = list(self.baseDirectoryMap)
            if len(bdKeys) == 1:
                self.baseDirectory = os.path.normpath(self.baseDirectoryMap[bdKeys[0]])
                self.overrideDataDirKey = bdKeys[0]
                self.baseDirectoryMap = {}
            elif len(bdKeys) > 1:
                self.multiRoot = True

    def getAbsolutePath(self, relativePath):
        absolutePath = None

        if self.multiRoot:
            relPathParts = relativePath.replace("\\", "/").split("/")
            realBasePath = self.baseDirectoryMap[relPathParts[0]]
            absolutePath = os.path.join(realBasePath, *relPathParts[1:])
        else:
            absolutePath = os.path.join(self.baseDirectory, relativePath)

        cleanedPath = os.path.normpath(absolutePath)

        # Make sure the cleanedPath is part of the allowed ones
        if self.multiRoot:
            for key, value in self.baseDirectoryMap.items():
                if cleanedPath.startswith(value):
                    return cleanedPath
        elif cleanedPath.startswith(self.baseDirectory):
            return cleanedPath

        return None

    def updateScalarBars(self, view=None, mode=1):
        """
        Manage scalarbar state

            view:
                A view proxy or the current active view will be used.

            mode:
                HIDE_UNUSED_SCALAR_BARS = 0x01,
                SHOW_USED_SCALAR_BARS = 0x02
        """
        v = view or self.getView(-1)
        lutMgr = vtkSMTransferFunctionManager()
        lutMgr.UpdateScalarBars(v.SMProxy, mode)

    def publish(self, topic, event):
        if self.coreServer:
            self.coreServer.publish(topic, event)
