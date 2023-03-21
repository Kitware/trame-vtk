import os
import re

from wslink import register as exportRpc

from .web_protocol import vtkWebProtocol


class vtkWebFileBrowser(vtkWebProtocol):
    """Provide File/Directory listing"""

    def __init__(
        self, basePath, name, excludeRegex=r"^\.|~$|^\$", groupRegex=r"[0-9]+\."
    ):
        """
        Configure the way the WebFile browser will expose the server content.
         - basePath: specify the base directory that we should start with
         - name: Name of that base directory that will show up on the web
         - excludeRegex: Regular expression of what should be excluded from the list of files/directories
        """
        self.baseDirectory = basePath
        self.rootName = name
        self.pattern = re.compile(excludeRegex)
        self.gPattern = re.compile(groupRegex)

    @exportRpc("file.server.directory.list")
    def listServerDirectory(self, relativeDir="."):
        """
        RPC Callback to list a server directory relative to the basePath
        provided at start-up.
        """
        path = [self.rootName]
        if len(relativeDir) > len(self.rootName):
            relativeDir = relativeDir[len(self.rootName) + 1 :]
            path += relativeDir.replace("\\", "/").split("/")

        currentPath = os.path.join(self.baseDirectory, relativeDir)
        result = {
            "label": relativeDir,
            "files": [],
            "dirs": [],
            "groups": [],
            "path": path,
        }
        if relativeDir == ".":
            result["label"] = self.rootName
        for file in os.listdir(currentPath):
            if os.path.isfile(os.path.join(currentPath, file)) and not re.search(
                self.pattern, file
            ):
                result["files"].append({"label": file, "size": -1})
            elif os.path.isdir(os.path.join(currentPath, file)) and not re.search(
                self.pattern, file
            ):
                result["dirs"].append(file)

        # Filter files to create groups
        files = result["files"]
        files.sort()
        groups = result["groups"]
        groupIdx = {}
        filesToRemove = []
        for file in files:
            fileSplit = re.split(self.gPattern, file["label"])
            if len(fileSplit) == 2:
                filesToRemove.append(file)
                gName = "*.".join(fileSplit)
                if gName in groupIdx:
                    groupIdx[gName]["files"].append(file["label"])
                else:
                    groupIdx[gName] = {"files": [file["label"]], "label": gName}
                    groups.append(groupIdx[gName])
        for file in filesToRemove:
            gName = "*.".join(re.split(self.gPattern, file["label"]))
            if len(groupIdx[gName]["files"]) > 1:
                files.remove(file)
            else:
                groups.remove(groupIdx[gName])

        return result
