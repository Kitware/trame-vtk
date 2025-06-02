from vtkmodules.vtkRenderingCore import vtkColorTransferFunction

from .helpers import data_table_to_list, linspace
from .registry import class_name
from .utils import reference_id
from .cache import cache_properties


def lookup_table_serializer(parent, lookup_table, lookup_table_id, context, depth):
    # No children in this case, so no additions to bindings and return empty list
    # But we do need to add instance

    lookup_table_range = lookup_table.GetRange()

    lookup_table_hue_range = [0.5, 0]
    if hasattr(lookup_table, "GetHueRange"):
        try:
            lookup_table.GetHueRange(lookup_table_hue_range)
        except Exception:
            pass

    lut_sat_range = lookup_table.GetSaturationRange()
    table = data_table_to_list(lookup_table.GetTable())
    properties = {
        "numberOfColors": lookup_table.GetNumberOfColors(),
        "valueRange": lookup_table_range,
        "hueRange": lookup_table_hue_range,
        # 'alpha_range': lut_alpha_range,  # Causes weird rendering artifacts on client
        "saturationRange": lut_sat_range,
        "nanColor": lookup_table.GetNanColor(),
        "belowRangeColor": lookup_table.GetBelowRangeColor(),
        "aboveRangeColor": lookup_table.GetAboveRangeColor(),
        "useAboveRangeColor": True if lookup_table.GetUseAboveRangeColor() else False,
        "useBelowRangeColor": True if lookup_table.GetUseBelowRangeColor() else False,
        "alpha": lookup_table.GetAlpha(),
        "vectorSize": lookup_table.GetVectorSize(),
        "vectorComponent": lookup_table.GetVectorComponent(),
        "vectorMode": lookup_table.GetVectorMode(),
        "indexedLookup": lookup_table.GetIndexedLookup(),
    }

    if table:
        properties["table"] = table

    return {
        "parent": reference_id(parent),
        "id": lookup_table_id,
        "type": class_name(lookup_table),
        "properties": cache_properties(lookup_table_id, context, properties),
    }


# -----------------------------------------------------------------------------


def lookup_table_to_color_transfer_function(lookup_table):
    data_table = lookup_table.GetTable()
    table = data_table_to_list(data_table)

    if not table:
        lookup_table.Build()
        table = data_table_to_list(data_table)

    if table:
        ctf = vtkColorTransferFunction()
        ctf.DeepCopy(lookup_table)  # <== needed to capture vector props

        table_range = lookup_table.GetTableRange()
        points = linspace(*table_range, num=len(table))
        for x, rgba in zip(points, table):
            ctf.AddRGBPoint(x, *[x / 255 for x in rgba[:3]])

        return ctf

    return None


def lookup_table_serializer2(parent, lookup_table, lookup_table_id, context, depth):
    ctf = lookup_table_to_color_transfer_function(lookup_table)
    if ctf:
        return color_transfer_function_serializer(
            parent, ctf, lookup_table_id, context, depth
        )

    return None


def color_transfer_function_serializer(parent, instance, obj_id, context, depth):
    nodes = []
    for i in range(instance.GetSize()):
        # x, r, g, b, midpoint, sharpness
        node = [0, 0, 0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    discretize = 0
    number_of_values = instance.GetSize()
    if hasattr(instance, "GetDiscretize"):
        discretize = (
            instance.GetDiscretize() if hasattr(instance, "GetDiscretize") else 0
        )
        number_of_values = (
            instance.GetNumberOfValues()
            if hasattr(instance, "GetNumberOfValues")
            else 256
        )

    return {
        "parent": reference_id(parent),
        "id": obj_id,
        "type": class_name(instance),
        "properties": cache_properties(
            obj_id,
            context,
            {
                "clamping": 1 if instance.GetClamping() else 0,
                "colorSpace": instance.GetColorSpace(),
                "hSVWrap": 1 if instance.GetHSVWrap() else 0,
                # 'nan_color': instance.GetNanColor(),                  # Breaks client
                # 'below_range_color': instance.GetBelowRangeColor(),    # Breaks client
                # 'above_range_color': instance.GetAboveRangeColor(),    # Breaks client
                # 'use_above_range_color': 1 if instance.GetUseAboveRangeColor() else 0,
                # 'use_below_range_color': 1 if instance.GetUseBelowRangeColor() else 0,
                "allowDuplicateScalars": 1
                if instance.GetAllowDuplicateScalars()
                else 0,
                "alpha": instance.GetAlpha(),
                "vectorComponent": instance.GetVectorComponent(),
                "vectorSize": instance.GetVectorSize(),
                "vectorMode": instance.GetVectorMode(),
                "indexedLookup": instance.GetIndexedLookup(),
                "nodes": nodes,
                "numberOfValues": number_of_values,
                "discretize": discretize,
            },
        ),
    }


def discretizable_color_transfer_function_serializer(
    parent, instance, obj_id, context, depth
):
    ctf = color_transfer_function_serializer(parent, instance, obj_id, context, depth)
    ctf["properties"]["discretize"] = instance.GetDiscretize()
    ctf["properties"]["numberOfValues"] = instance.GetNumberOfValues()
    return ctf


def pwf_serializer(parent, instance, obj_id, context, depth):
    nodes = []

    for i in range(instance.GetSize()):
        # x, y, midpoint, sharpness
        node = [0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    return {
        "parent": reference_id(parent),
        "id": obj_id,
        "type": class_name(instance),
        "properties": cache_properties(
            obj_id,
            context,
            {
                "range": list(instance.GetRange()),
                "clamping": instance.GetClamping(),
                "allowDuplicateScalars": instance.GetAllowDuplicateScalars(),
                "nodes": nodes,
            },
        ),
    }
