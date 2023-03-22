from .registry import class_name
from .utils import getReferenceId


def pwfSerializer(parent, instance, objId, context, depth):
    nodes = []

    for i in range(instance.GetSize()):
        # x, y, midpoint, sharpness
        node = [0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    return {
        "parent": getReferenceId(parent),
        "id": objId,
        "type": class_name(instance),
        "properties": {
            "range": list(instance.GetRange()),
            "clamping": instance.GetClamping(),
            "allowDuplicateScalars": instance.GetAllowDuplicateScalars(),
            "nodes": nodes,
        },
    }
