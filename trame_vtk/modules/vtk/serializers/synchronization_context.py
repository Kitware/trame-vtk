import io
import logging
import time
import zipfile

from vtkmodules.vtkCommonCore import vtkTypeUInt32Array

from .utils import base64Encode, wrapId

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class SynchronizationContext:
    """Convenience class for caching data arrays, storing computed sha sums, keeping
    track of valid actors, etc..
    """

    def __init__(self):
        self.dataArrayCache = {}
        self.lastDependenciesMapping = {}
        self.ingoreLastDependencies = False

    def setIgnoreLastDependencies(self, force):
        self.ingoreLastDependencies = force

    def cacheDataArray(self, pMd5, data):
        self.dataArrayCache[pMd5] = data

    def getCachedDataArray(self, pMd5, binary=False, compression=False):
        cacheObj = self.dataArrayCache[pMd5]
        array = cacheObj["array"]
        cacheTime = cacheObj["mTime"]

        if cacheTime != array.GetMTime():
            logger.debug(" ***** ERROR: you asked for an old cache key! ***** ")

        if array.GetDataType() == 12:
            # IdType need to be converted to Uint32
            arraySize = array.GetNumberOfTuples() * array.GetNumberOfComponents()
            newArray = vtkTypeUInt32Array()
            newArray.SetNumberOfTuples(arraySize)
            for i in range(arraySize):
                newArray.SetValue(i, -1 if array.GetValue(i) < 0 else array.GetValue(i))
            pBuffer = memoryview(newArray)
        else:
            pBuffer = memoryview(array)

        if binary:
            # Convert the vtkUnsignedCharArray into a bytes object, required by
            # Autobahn websockets
            return (
                pBuffer.tobytes()
                if not compression
                else zipCompression(pMd5, pBuffer.tobytes())
            )

        return base64Encode(
            pBuffer if not compression else zipCompression(pMd5, pBuffer.tobytes())
        )

    def checkForArraysToRelease(self, timeWindow=20):
        cutOffTime = time.time() - timeWindow
        shasToDelete = []
        for sha in self.dataArrayCache:
            record = self.dataArrayCache[sha]
            array = record["array"]
            count = array.GetReferenceCount()

            if count == 1 and record["ts"] < cutOffTime:
                shasToDelete.append(sha)

        for sha in shasToDelete:
            del self.dataArrayCache[sha]

    def getLastDependencyList(self, idstr):
        lastDeps = []
        if idstr in self.lastDependenciesMapping and not self.ingoreLastDependencies:
            lastDeps = self.lastDependenciesMapping[idstr]
        return lastDeps

    def setNewDependencyList(self, idstr, depList):
        self.lastDependenciesMapping[idstr] = depList

    def buildDependencyCallList(self, idstr, newList, addMethod, removeMethod):
        oldList = self.getLastDependencyList(idstr)

        calls = []
        calls += [[addMethod, [wrapId(x)]] for x in newList if x not in oldList]
        calls += [[removeMethod, [wrapId(x)]] for x in oldList if x not in newList]

        self.setNewDependencyList(idstr, newList)
        return calls


def zipCompression(name, data):
    with io.BytesIO() as in_memory:
        with zipfile.ZipFile(in_memory, mode="w") as zf:
            zf.writestr("data/%s" % name, data, zipfile.ZIP_DEFLATED)
        in_memory.seek(0)
        return in_memory.read()
