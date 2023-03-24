import logging

from .serialize import serialize
from .utils import reference_id, wrap_id

logger = logging.getLogger(__name__)


def texture_serializer(parent, texture, texture_id, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    data_object = None
    data_object_instance = None
    calls = []
    dependencies = []

    if hasattr(texture, "GetInput"):
        data_object = texture.GetInput()
    else:
        logger.debug("This texture does not have GetInput method")

    if data_object:
        data_object_id = "%s-texture" % texture_id
        data_object_instance = serialize(
            texture, data_object, data_object_id, context, depth + 1
        )
        if data_object_instance:
            dependencies.append(data_object_instance)
            calls.append(["setInputData", [wrap_id(data_object_id)]])

    if data_object_instance:
        return {
            "parent": reference_id(parent),
            "id": texture_id,
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
