from .registry import class_name
from .utils import reference_id
from .cache import cache_properties


def light_type_to_string(value):
    """
    #define VTK_LIGHT_TYPE_HEADLIGHT    1
    #define VTK_LIGHT_TYPE_CAMERA_LIGHT 2
    #define VTK_LIGHT_TYPE_SCENE_LIGHT  3

    'HeadLight';
    'SceneLight';
    'CameraLight'
    """
    if value == 1:
        return "HeadLight"
    elif value == 2:
        return "CameraLight"

    return "SceneLight"


def light_serializer(parent, instance, obj_id, context, depth):
    return {
        "parent": reference_id(parent),
        "id": obj_id,
        "type": class_name(instance),
        "properties": cache_properties(
            obj_id,
            context,
            {
                # 'specular_color': instance.GetSpecularColor(),
                # 'ambient_color': instance.GetAmbientColor(),
                "switch": instance.GetSwitch(),
                "intensity": instance.GetIntensity(),
                "color": instance.GetDiffuseColor(),
                "position": instance.GetPosition(),
                "focalPoint": instance.GetFocalPoint(),
                "positional": instance.GetPositional(),
                "exponent": instance.GetExponent(),
                "coneAngle": instance.GetConeAngle(),
                "attenuationValues": instance.GetAttenuationValues(),
                "lightType": light_type_to_string(instance.GetLightType()),
                "shadowAttenuation": instance.GetShadowAttenuation(),
            },
        ),
    }
