from .registry import class_name
from .serialize import serialize
from .utils import reference_id, wrap_id
from .cache import cache_properties


def property_serializer(parent, prop_obj, prop_obj_id, context, depth):
    representation = (
        prop_obj.GetRepresentation() if hasattr(prop_obj, "GetRepresentation") else 2
    )
    color_to_use = (
        prop_obj.GetDiffuseColor()
        if hasattr(prop_obj, "GetDiffuseColor")
        else [1, 1, 1]
    )
    if representation == 1 and hasattr(prop_obj, "GetColor"):
        color_to_use = prop_obj.GetColor()

    return {
        "parent": reference_id(parent),
        "id": prop_obj_id,
        "type": class_name(prop_obj),
        "properties": cache_properties(
            prop_obj_id,
            context,
            {
                "representation": representation,
                "diffuseColor": color_to_use,
                "color": prop_obj.GetColor(),
                "ambientColor": prop_obj.GetAmbientColor(),
                "specularColor": prop_obj.GetSpecularColor(),
                "edgeColor": prop_obj.GetEdgeColor(),
                "ambient": prop_obj.GetAmbient(),
                "diffuse": prop_obj.GetDiffuse(),
                "specular": prop_obj.GetSpecular(),
                "specularPower": prop_obj.GetSpecularPower(),
                "opacity": prop_obj.GetOpacity(),
                "interpolation": prop_obj.GetInterpolation(),
                "edgeVisibility": 1 if prop_obj.GetEdgeVisibility() else 0,
                "backfaceCulling": 1 if prop_obj.GetBackfaceCulling() else 0,
                "frontfaceCulling": 1 if prop_obj.GetFrontfaceCulling() else 0,
                "pointSize": prop_obj.GetPointSize(),
                "lineWidth": prop_obj.GetLineWidth(),
                "lighting": 1 if prop_obj.GetLighting() else 0,
            },
        ),
    }


def volume_property_serializer(parent, prop_obj, prop_obj_id, context, depth):
    calls = []
    dependencies = []

    # Color handling
    lut = prop_obj.GetRGBTransferFunction()
    if lut:
        lookup_table_id = reference_id(lut)
        lookup_table_instance = serialize(
            prop_obj, lut, lookup_table_id, context, depth + 1
        )

        if lookup_table_instance:
            dependencies.append(lookup_table_instance)
            calls.append(["setRGBTransferFunction", [0, wrap_id(lookup_table_id)]])

    # Piecewise handling
    pwf = prop_obj.GetScalarOpacity()
    if pwf:
        pwf_id = reference_id(pwf)
        pwf_instance = serialize(prop_obj, pwf, pwf_id, context, depth + 1)

        if pwf_instance:
            dependencies.append(pwf_instance)
            calls.append(["setScalarOpacity", [0, wrap_id(pwf_id)]])

    return {
        "parent": reference_id(parent),
        "id": prop_obj_id,
        "type": class_name(prop_obj),
        "properties": {
            "independentComponents": prop_obj.GetIndependentComponents(),
            "interpolationType": prop_obj.GetInterpolationType(),
            "shade": prop_obj.GetShade(),
            "ambient": prop_obj.GetAmbient(),
            "diffuse": prop_obj.GetDiffuse(),
            "specular": prop_obj.GetSpecular(),
            "specularPower": prop_obj.GetSpecularPower(),
            # "useLabelOutline": prop_obj.GetUseLabelOutline(),
            # "labelOutlineThickness": prop_obj.GetLabelOutlineThickness(),
        },
        "calls": calls,
        "dependencies": dependencies,
    }
