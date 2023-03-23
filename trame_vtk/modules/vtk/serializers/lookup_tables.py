from vtkmodules.vtkRenderingCore import vtkColorTransferFunction

from .helpers import dataTableToList, linspace
from .registry import class_name
from .utils import getReferenceId


def lookupTableSerializer(parent, lookupTable, lookupTableId, context, depth):
    # No children in this case, so no additions to bindings and return empty list
    # But we do need to add instance

    lookupTableRange = lookupTable.GetRange()

    lookupTableHueRange = [0.5, 0]
    if hasattr(lookupTable, "GetHueRange"):
        try:
            lookupTable.GetHueRange(lookupTableHueRange)
        except Exception:
            pass

    lutSatRange = lookupTable.GetSaturationRange()

    return {
        "parent": getReferenceId(parent),
        "id": lookupTableId,
        "type": class_name(lookupTable),
        "properties": {
            "numberOfColors": lookupTable.GetNumberOfColors(),
            "valueRange": lookupTableRange,
            "hueRange": lookupTableHueRange,
            # 'alphaRange': lutAlphaRange,  # Causes weird rendering artifacts on client
            "saturationRange": lutSatRange,
            "nanColor": lookupTable.GetNanColor(),
            "belowRangeColor": lookupTable.GetBelowRangeColor(),
            "aboveRangeColor": lookupTable.GetAboveRangeColor(),
            "useAboveRangeColor": True
            if lookupTable.GetUseAboveRangeColor()
            else False,
            "useBelowRangeColor": True
            if lookupTable.GetUseBelowRangeColor()
            else False,
            "alpha": lookupTable.GetAlpha(),
            "vectorSize": lookupTable.GetVectorSize(),
            "vectorComponent": lookupTable.GetVectorComponent(),
            "vectorMode": lookupTable.GetVectorMode(),
            "indexedLookup": lookupTable.GetIndexedLookup(),
        },
    }


# -----------------------------------------------------------------------------


def lookupTableToColorTransferFunction(lookupTable):
    dataTable = lookupTable.GetTable()
    table = dataTableToList(dataTable)

    if not table:
        lookupTable.Build()
        table = dataTableToList(dataTable)

    if table:
        ctf = vtkColorTransferFunction()
        ctf.DeepCopy(lookupTable)  # <== needed to capture vector props

        tableRange = lookupTable.GetTableRange()
        points = linspace(*tableRange, num=len(table))
        for x, rgba in zip(points, table):
            ctf.AddRGBPoint(x, *[x / 255 for x in rgba[:3]])

        return ctf

    return None


def lookupTableSerializer2(parent, lookupTable, lookupTableId, context, depth):
    ctf = lookupTableToColorTransferFunction(lookupTable)
    if ctf:
        return colorTransferFunctionSerializer(
            parent, ctf, lookupTableId, context, depth
        )

    return None


def colorTransferFunctionSerializer(parent, instance, objId, context, depth):
    nodes = []
    for i in range(instance.GetSize()):
        # x, r, g, b, midpoint, sharpness
        node = [0, 0, 0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    discretize = 0
    numberOfValues = instance.GetSize()
    if hasattr(instance, "GetDiscretize"):
        discretize = (
            instance.GetDiscretize() if hasattr(instance, "GetDiscretize") else 0
        )
        numberOfValues = (
            instance.GetNumberOfValues()
            if hasattr(instance, "GetNumberOfValues")
            else 256
        )
    elif numberOfValues < 256:
        discretize = 1

    return {
        "parent": getReferenceId(parent),
        "id": objId,
        "type": class_name(instance),
        "properties": {
            "clamping": 1 if instance.GetClamping() else 0,
            "colorSpace": instance.GetColorSpace(),
            "hSVWrap": 1 if instance.GetHSVWrap() else 0,
            # 'nanColor': instance.GetNanColor(),                  # Breaks client
            # 'belowRangeColor': instance.GetBelowRangeColor(),    # Breaks client
            # 'aboveRangeColor': instance.GetAboveRangeColor(),    # Breaks client
            # 'useAboveRangeColor': 1 if instance.GetUseAboveRangeColor() else 0,
            # 'useBelowRangeColor': 1 if instance.GetUseBelowRangeColor() else 0,
            "allowDuplicateScalars": 1 if instance.GetAllowDuplicateScalars() else 0,
            "alpha": instance.GetAlpha(),
            "vectorComponent": instance.GetVectorComponent(),
            "vectorSize": instance.GetVectorSize(),
            "vectorMode": instance.GetVectorMode(),
            "indexedLookup": instance.GetIndexedLookup(),
            "nodes": nodes,
            "numberOfValues": numberOfValues,
            "discretize": discretize,
        },
    }


def discretizableColorTransferFunctionSerializer(
    parent, instance, objId, context, depth
):
    ctf = colorTransferFunctionSerializer(parent, instance, objId, context, depth)
    ctf["properties"]["discretize"] = instance.GetDiscretize()
    ctf["properties"]["numberOfValues"] = instance.GetNumberOfValues()
    return ctf


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
