from .registry import class_name
from .serialize import serialize
from .utils import getReferenceId, wrapId


def propertySerializer(parent, propObj, propObjId, context, depth):
    representation = (
        propObj.GetRepresentation() if hasattr(propObj, "GetRepresentation") else 2
    )
    colorToUse = (
        propObj.GetDiffuseColor() if hasattr(propObj, "GetDiffuseColor") else [1, 1, 1]
    )
    if representation == 1 and hasattr(propObj, "GetColor"):
        colorToUse = propObj.GetColor()

    return {
        "parent": getReferenceId(parent),
        "id": propObjId,
        "type": class_name(propObj),
        "properties": {
            "representation": representation,
            "diffuseColor": colorToUse,
            "color": propObj.GetColor(),
            "ambientColor": propObj.GetAmbientColor(),
            "specularColor": propObj.GetSpecularColor(),
            "edgeColor": propObj.GetEdgeColor(),
            "ambient": propObj.GetAmbient(),
            "diffuse": propObj.GetDiffuse(),
            "specular": propObj.GetSpecular(),
            "specularPower": propObj.GetSpecularPower(),
            "opacity": propObj.GetOpacity(),
            "interpolation": propObj.GetInterpolation(),
            "edgeVisibility": 1 if propObj.GetEdgeVisibility() else 0,
            "backfaceCulling": 1 if propObj.GetBackfaceCulling() else 0,
            "frontfaceCulling": 1 if propObj.GetFrontfaceCulling() else 0,
            "pointSize": propObj.GetPointSize(),
            "lineWidth": propObj.GetLineWidth(),
            "lighting": 1 if propObj.GetLighting() else 0,
        },
    }


def volumePropertySerializer(parent, propObj, propObjId, context, depth):
    calls = []
    dependencies = []

    # Color handling
    lut = propObj.GetRGBTransferFunction()
    if lut:
        lookupTableId = getReferenceId(lut)
        lookupTableInstance = serialize(propObj, lut, lookupTableId, context, depth + 1)

        if lookupTableInstance:
            dependencies.append(lookupTableInstance)
            calls.append(["setRGBTransferFunction", [0, wrapId(lookupTableId)]])

    # Piecewise handling
    pwf = propObj.GetScalarOpacity()
    if pwf:
        pwfId = getReferenceId(pwf)
        pwfInstance = serialize(propObj, pwf, pwfId, context, depth + 1)

        if pwfInstance:
            dependencies.append(pwfInstance)
            calls.append(["setScalarOpacity", [0, wrapId(pwfId)]])

    return {
        "parent": getReferenceId(parent),
        "id": propObjId,
        "type": class_name(propObj),
        "properties": {
            "independentComponents": propObj.GetIndependentComponents(),
            "interpolationType": propObj.GetInterpolationType(),
            "shade": propObj.GetShade(),
            "ambient": propObj.GetAmbient(),
            "diffuse": propObj.GetDiffuse(),
            "specular": propObj.GetSpecular(),
            "specularPower": propObj.GetSpecularPower(),
            # "useLabelOutline": propObj.GetUseLabelOutline(),
            # "labelOutlineThickness": propObj.GetLabelOutlineThickness(),
        },
        "calls": calls,
        "dependencies": dependencies,
    }
