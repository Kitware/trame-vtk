import logging

from .registry import class_name
from .serialize import serialize
from .utils import reference_id, rgb_float_to_hex, wrap_id
from .cache import cache_properties

logger = logging.getLogger(__name__)


def generic_actor_serializer(parent, actor, actor_id, context, depth):
    # This kind of actor has two "children" of interest, a property and a
    # mapper
    actor_visibility = actor.GetVisibility()
    mapper_instance = None
    property_instance = None
    calls = []
    dependencies = []
    add_on = {}

    if actor_visibility:
        mapper = None
        if not hasattr(actor, "GetMapper"):
            logger.debug("This actor does not have a GetMapper method")
        else:
            mapper = actor.GetMapper()

        if mapper:
            mapper_id = reference_id(mapper)
            mapper_instance = serialize(actor, mapper, mapper_id, context, depth + 1)
            if mapper_instance:
                dependencies.append(mapper_instance)
                calls.append(["setMapper", [wrap_id(mapper_id)]])

        prop = None
        if hasattr(actor, "GetProperty"):
            prop = actor.GetProperty()
        else:
            logger.debug("This actor does not have a GetProperty method")

        if prop:
            prop_id = reference_id(prop)
            property_instance = serialize(actor, prop, prop_id, context, depth + 1)
            if property_instance:
                dependencies.append(property_instance)
                calls.append(["setProperty", [wrap_id(prop_id)]])

        # Handle texture if any
        texture = None
        if hasattr(actor, "GetTexture"):
            texture = actor.GetTexture()
        else:
            logger.debug("This actor does not have a GetTexture method")

        if texture:
            texture_id = reference_id(texture)
            texture_instance = serialize(actor, texture, texture_id, context, depth + 1)
            if texture_instance:
                dependencies.append(texture_instance)
                calls.append(["addTexture", [wrap_id(texture_id)]])

    # Apply transform
    if actor.GetUserMatrix():
        user_matrix = [0] * 16
        matrix = actor.GetUserMatrix()
        for i in range(4):
            for j in range(4):
                idx = i + 4 * j
                user_matrix[idx] = matrix.GetElement(i, j)
        add_on["userMatrix"] = user_matrix

    if actor_visibility == 0 or (mapper_instance and property_instance):
        return {
            "parent": reference_id(parent),
            "id": actor_id,
            "type": class_name(actor),
            "properties": cache_properties(
                actor_id,
                context,
                {
                    # vtkProp
                    "visibility": actor_visibility,
                    "pickable": actor.GetPickable(),
                    "dragable": actor.GetDragable(),
                    "useBounds": actor.GetUseBounds(),
                    # vtkProp3D
                    "origin": actor.GetOrigin(),
                    "position": actor.GetPosition(),
                    "scale": actor.GetScale(),
                    "orientation": actor.GetOrientation(),
                    # vtkActor
                    "forceOpaque": actor.GetForceOpaque(),
                    "forceTranslucent": actor.GetForceTranslucent(),
                    # additional properties
                    **add_on,
                },
            ),
            "calls": calls,
            "dependencies": dependencies,
        }

    return None


# -----------------------------------------------------------------------------


def cube_axes_serializer(parent, actor, actor_id, context, depth):
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
    axis_labels = ["", "", ""]
    if actor.GetXAxisLabelVisibility():
        axis_labels[0] = actor.GetXTitle()
    if actor.GetYAxisLabelVisibility():
        axis_labels[1] = actor.GetYTitle()
    if actor.GetZAxisLabelVisibility():
        axis_labels[2] = actor.GetZTitle()

    text_color = rgb_float_to_hex(*actor.GetXAxesGridlinesProperty().GetColor())

    dependencies = []
    calls = [
        [
            "setCamera",
            [wrap_id(reference_id(actor.GetCamera()))],
        ]
    ]

    prop = None
    if hasattr(actor, "GetXAxesLinesProperty"):
        prop = actor.GetXAxesLinesProperty()
    else:
        logger.debug("This actor does not have a GetXAxesLinesProperty method")

    if prop:
        prop_id = reference_id(prop)
        property_instance = serialize(actor, prop, prop_id, context, depth + 1)
        if property_instance:
            dependencies.append(property_instance)
            calls.append(["setProperty", [wrap_id(prop_id)]])

    return {
        "parent": reference_id(parent),
        "id": actor_id,
        "type": "vtkCubeAxesActor",
        "properties": cache_properties(
            actor_id,
            context,
            {
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
                "axisLabels": axis_labels,
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
        ),
        "calls": calls,
        "dependencies": dependencies,
    }


# -----------------------------------------------------------------------------


def scalar_bar_actor_serializer(parent, actor, actor_id, context, depth):
    dependencies = []
    calls = []
    lut = actor.GetLookupTable()
    if not lut:
        return None

    lut_id = reference_id(lut)
    lut_instance = serialize(actor, lut, lut_id, context, depth + 1)
    if not lut_instance:
        return None

    dependencies.append(lut_instance)
    calls.append(["setScalarsToColors", [wrap_id(lut_id)]])

    prop = None
    if hasattr(actor, "GetProperty"):
        prop = actor.GetProperty()
    else:
        if context.debug_all:
            print("This scalar_bar_actor does not have a GetProperty method")

        if prop:
            prop_id = reference_id(prop)
            property_instance = serialize(actor, prop, prop_id, context, depth + 1)
            if property_instance:
                dependencies.append(property_instance)
                calls.append(["setProperty", [wrap_id(prop_id)]])

    axis_label = actor.GetTitle()
    width = actor.GetWidth()
    height = actor.GetHeight()

    return {
        "parent": reference_id(parent),
        "id": actor_id,
        "type": "vtkScalarBarActor",
        "properties": cache_properties(
            actor_id,
            context,
            {
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
                "axisLabel": axis_label,
                # 'bar_position': [0, 0],
                # 'bar_size': [0, 0],
                "boxPosition": [0.88, -0.92],
                "boxSize": [width, height],
                "axisTitlePixelOffset": 36.0,
                "axisTextStyle": {
                    "fontColor": rgb_float_to_hex(
                        *actor.GetTitleTextProperty().GetColor()
                    ),
                    "fontStyle": "normal",
                    "fontSize": 18,
                    "fontFamily": "serif",
                },
                "tickLabelPixelOffset": 14.0,
                "tickTextStyle": {
                    "fontColor": rgb_float_to_hex(
                        *actor.GetTitleTextProperty().GetColor()
                    ),
                    "fontStyle": "normal",
                    "fontSize": 14,
                    "fontFamily": "serif",
                },
                "drawNanAnnotation": actor.GetDrawNanAnnotation(),
                "drawBelowRangeSwatch": actor.GetDrawBelowRangeSwatch(),
                "drawAboveRangeSwatch": actor.GetDrawAboveRangeSwatch(),
            },
        ),
        "calls": calls,
        "dependencies": dependencies,
    }


# -----------------------------------------------------------------------------


def axes_actor_serializer(parent, actor, actor_id, context, depth):
    actor_visibility = actor.GetVisibility()

    if not actor_visibility:
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
    if actor.GetUserMatrix():
        matrix = actor.GetUserMatrix()
        matrix.Transpose()
        for i in range(4):
            for j in range(4):
                idx = i + 4 * j
                user_matrix[idx] = matrix.GetElement(j, i)

    return {
        "parent": reference_id(parent),
        "id": actor_id,
        "type": "vtkAxesActor",
        "properties": cache_properties(
            actor_id,
            context,
            {
                # vtkProp
                "visibility": actor_visibility,
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
        ),
    }
