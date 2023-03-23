import logging

from vtkmodules.vtkCommonMath import vtkMatrix4x4

from .registry import class_name
from .serialize import serialize
from .utils import getReferenceId, rgb_float_to_hex, wrapId

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def genericActorSerializer(parent, actor, actorId, context, depth):
    # This kind of actor has two "children" of interest, a property and a
    # mapper
    actorVisibility = actor.GetVisibility()
    mapperInstance = None
    propertyInstance = None
    calls = []
    dependencies = []

    if actorVisibility:
        mapper = None
        if not hasattr(actor, "GetMapper"):
            logger.debug("This actor does not have a GetMapper method")
        else:
            mapper = actor.GetMapper()

        if mapper:
            mapperId = getReferenceId(mapper)
            mapperInstance = serialize(actor, mapper, mapperId, context, depth + 1)
            if mapperInstance:
                dependencies.append(mapperInstance)
                calls.append(["setMapper", [wrapId(mapperId)]])

        prop = None
        if hasattr(actor, "GetProperty"):
            prop = actor.GetProperty()
        else:
            logger.debug("This actor does not have a GetProperty method")

        if prop:
            propId = getReferenceId(prop)
            propertyInstance = serialize(actor, prop, propId, context, depth + 1)
            if propertyInstance:
                dependencies.append(propertyInstance)
                calls.append(["setProperty", [wrapId(propId)]])

        # Handle texture if any
        texture = None
        if hasattr(actor, "GetTexture"):
            texture = actor.GetTexture()
        else:
            logger.debug("This actor does not have a GetTexture method")

        if texture:
            textureId = getReferenceId(texture)
            textureInstance = serialize(actor, texture, textureId, context, depth + 1)
            if textureInstance:
                dependencies.append(textureInstance)
                calls.append(["addTexture", [wrapId(textureId)]])

    if actorVisibility == 0 or (mapperInstance and propertyInstance):
        return {
            "parent": getReferenceId(parent),
            "id": actorId,
            "type": class_name(actor),
            "properties": {
                # vtkProp
                "visibility": actorVisibility,
                "pickable": actor.GetPickable(),
                "dragable": actor.GetDragable(),
                "useBounds": actor.GetUseBounds(),
                # vtkProp3D
                "origin": actor.GetOrigin(),
                "position": actor.GetPosition(),
                "scale": actor.GetScale(),
                # vtkActor
                "forceOpaque": actor.GetForceOpaque(),
                "forceTranslucent": actor.GetForceTranslucent(),
            },
            "calls": calls,
            "dependencies": dependencies,
        }

    return None


# -----------------------------------------------------------------------------


def cubeAxesSerializer(parent, actor, actorId, context, depth):
    """
    Possible add-on properties for vtk.js:
        gridLines: True,
        axisLabels: None,
        axisTitlePixelOffset: 35.0,
        axisTextStyle: {
            fontColor: 'white',
            fontStyle: 'normal',
            fontSize: 18,
            fontFamily: 'serif',
        },
        tickLabelPixelOffset: 12.0,
        tickTextStyle: {
            fontColor: 'white',
            fontStyle: 'normal',
            fontSize: 14,
            fontFamily: 'serif',
        },
    """
    axisLabels = ["", "", ""]
    if actor.GetXAxisLabelVisibility():
        axisLabels[0] = actor.GetXTitle()
    if actor.GetYAxisLabelVisibility():
        axisLabels[1] = actor.GetYTitle()
    if actor.GetZAxisLabelVisibility():
        axisLabels[2] = actor.GetZTitle()

    text_color = rgb_float_to_hex(*actor.GetXAxesGridlinesProperty().GetColor())

    dependencies = []
    calls = [
        [
            "setCamera",
            [wrapId(getReferenceId(actor.GetCamera()))],
        ]
    ]

    prop = None
    if hasattr(actor, "GetXAxesLinesProperty"):
        prop = actor.GetXAxesLinesProperty()
    else:
        logger.debug("This actor does not have a GetXAxesLinesProperty method")

    if prop:
        propId = getReferenceId(prop)
        propertyInstance = serialize(actor, prop, propId, context, depth + 1)
        if propertyInstance:
            dependencies.append(propertyInstance)
            calls.append(["setProperty", [wrapId(propId)]])

    return {
        "parent": getReferenceId(parent),
        "id": actorId,
        "type": "vtkCubeAxesActor",
        "properties": {
            # vtkProp
            "visibility": actor.GetVisibility(),
            "pickable": actor.GetPickable(),
            "dragable": actor.GetDragable(),
            "useBounds": actor.GetUseBounds(),
            # vtkProp3D
            "origin": actor.GetOrigin(),
            "position": actor.GetPosition(),
            "scale": actor.GetScale(),
            # vtkActor
            "forceOpaque": actor.GetForceOpaque(),
            "forceTranslucent": actor.GetForceTranslucent(),
            # vtkCubeAxesActor
            "dataBounds": actor.GetBounds(),
            "faceVisibilityAngle": 8,
            "gridLines": True,
            "axisLabels": axisLabels,
            "axisTitlePixelOffset": 35.0,
            "axisTextStyle": {
                "fontColor": text_color,
                "fontStyle": "normal",
                "fontSize": 18,
                "fontFamily": "serif",
            },
            "tickLabelPixelOffset": 12.0,
            "tickTextStyle": {
                "fontColor": text_color,
                "fontStyle": "normal",
                "fontSize": 14,
                "fontFamily": "serif",
            },
        },
        "calls": calls,
        "dependencies": dependencies,
    }


# -----------------------------------------------------------------------------


def scalarBarActorSerializer(parent, actor, actorId, context, depth):
    dependencies = []
    calls = []
    lut = actor.GetLookupTable()
    if not lut:
        return None

    lutId = getReferenceId(lut)
    lutInstance = serialize(actor, lut, lutId, context, depth + 1)
    if not lutInstance:
        return None

    dependencies.append(lutInstance)
    calls.append(["setScalarsToColors", [wrapId(lutId)]])

    prop = None
    if hasattr(actor, "GetProperty"):
        prop = actor.GetProperty()
    else:
        if context.debugAll:
            print("This scalarBarActor does not have a GetProperty method")

        if prop:
            propId = getReferenceId(prop)
            propertyInstance = serialize(actor, prop, propId, context, depth + 1)
            if propertyInstance:
                dependencies.append(propertyInstance)
                calls.append(["setProperty", [wrapId(propId)]])

    axisLabel = actor.GetTitle()
    width = actor.GetWidth()
    height = actor.GetHeight()

    return {
        "parent": getReferenceId(parent),
        "id": actorId,
        "type": "vtkScalarBarActor",
        "properties": {
            # vtkProp
            "visibility": actor.GetVisibility(),
            "pickable": actor.GetPickable(),
            "dragable": actor.GetDragable(),
            "useBounds": actor.GetUseBounds(),
            # vtkActor2D
            # "position": actor.GetPosition(),
            # "position2": actor.GetPosition2(),
            # "width": actor.GetWidth(),
            # "height": actor.GetHeight(),
            # vtkScalarBarActor
            "automated": True,
            "axisLabel": axisLabel,
            # 'barPosition': [0, 0],
            # 'barSize': [0, 0],
            "boxPosition": [0.88, -0.92],
            "boxSize": [width, height],
            "axisTitlePixelOffset": 36.0,
            "axisTextStyle": {
                "fontColor": rgb_float_to_hex(*actor.GetTitleTextProperty().GetColor()),
                "fontStyle": "normal",
                "fontSize": 18,
                "fontFamily": "serif",
            },
            "tickLabelPixelOffset": 14.0,
            "tickTextStyle": {
                "fontColor": rgb_float_to_hex(*actor.GetTitleTextProperty().GetColor()),
                "fontStyle": "normal",
                "fontSize": 14,
                "fontFamily": "serif",
            },
            "drawNanAnnotation": actor.GetDrawNanAnnotation(),
            "drawBelowRangeSwatch": actor.GetDrawBelowRangeSwatch(),
            "drawAboveRangeSwatch": actor.GetDrawAboveRangeSwatch(),
        },
        "calls": calls,
        "dependencies": dependencies,
    }


# -----------------------------------------------------------------------------


def axesActorSerializer(parent, actor, actorId, context, depth):
    actorVisibility = actor.GetVisibility()

    if not actorVisibility:
        return None

    # C++ extract
    label_show = actor.GetAxisLabels()
    # label_position = actor.GetNormalizedLabelPosition()

    # shaft_length = actor.GetNormalizedShaftLength()
    shaft_type = actor.GetShaftType()  # int [line/cylinder]

    tip_length = actor.GetNormalizedTipLength()
    # tip_type = actor.GetTipType() # int [cone/sphere]

    cone_resolution = actor.GetConeResolution()
    cone_radius = actor.GetConeRadius()

    cylinder_resolution = actor.GetCylinderResolution()
    cylinder_radius = actor.GetCylinderRadius()

    # sphere_radius = actor.GetSphereRadius()
    # sphere_resolution = actor.GetSphereResolution()

    # XYZ...
    # actor.GetXAxisCaptionActor2D()
    # actor.GetXAxisTipProperty()
    # actor.GetXAxisShaftProperty()
    # actor.GetXAxisLabelText()

    # Apply transform
    user_matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    if actor.GetUserTransform():
        matrix = vtkMatrix4x4()
        actor.GetUserTransform().GetTranspose(matrix)
        for i in range(4):
            for j in range(4):
                idx = i + 4 * j
                user_matrix[idx] = matrix.GetElement(j, i)

    return {
        "parent": getReferenceId(parent),
        "id": actorId,
        "type": "vtkAxesActor",
        "properties": {
            # vtkProp
            "visibility": actorVisibility,
            "pickable": actor.GetPickable(),
            "dragable": actor.GetDragable(),
            "useBounds": actor.GetUseBounds(),
            # vtkProp3D
            "origin": actor.GetOrigin(),
            "position": actor.GetPosition(),
            "scale": actor.GetScale(),
            "userMatrix": user_matrix,
            # vtkAxesActor
            "labels": {
                "show": label_show,
                "x": actor.GetXAxisLabelText(),
                "y": actor.GetYAxisLabelText(),
                "z": actor.GetZAxisLabelText(),
            },
            "config": {
                "recenter": 0,
                "tipResolution": cone_resolution,  # 60,
                "tipRadius": 0.2 * cone_radius,  # 0.1,
                "tipLength": tip_length[0],  # 0.2,
                "shaftResolution": cylinder_resolution,  # 60,
                "shaftRadius": 0.01 if shaft_type else cylinder_radius,  # 0.03,
                "invert": 0,
            },
            "xAxisColor": list(
                map(lambda x: int(x * 255), actor.GetXAxisTipProperty().GetColor())
            ),
            "yAxisColor": list(
                map(lambda x: int(x * 255), actor.GetYAxisTipProperty().GetColor())
            ),
            "zAxisColor": list(
                map(lambda x: int(x * 255), actor.GetZAxisTipProperty().GetColor())
            ),
        },
    }
