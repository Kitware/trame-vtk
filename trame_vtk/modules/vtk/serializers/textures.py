import logging

from .serialize import serialize
from .utils import getReferenceId, wrapId

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def textureSerializer(parent, texture, textureId, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    dataObject = None
    dataObjectInstance = None
    calls = []
    dependencies = []

    if hasattr(texture, "GetInput"):
        dataObject = texture.GetInput()
    else:
        logger.debug("This texture does not have GetInput method")

    if dataObject:
        dataObjectId = "%s-texture" % textureId
        dataObjectInstance = serialize(
            texture, dataObject, dataObjectId, context, depth + 1
        )
        if dataObjectInstance:
            dependencies.append(dataObjectInstance)
            calls.append(["setInputData", [wrapId(dataObjectId)]])

    if dataObjectInstance:
        return {
            "parent": getReferenceId(parent),
            "id": textureId,
            "type": "vtkTexture",
            "properties": {
                "interpolate": texture.GetInterpolate(),
                "repeat": texture.GetRepeat(),
                "edgeClamp": texture.GetEdgeClamp(),
            },
            "calls": calls,
            "dependencies": dependencies,
        }

    return None
