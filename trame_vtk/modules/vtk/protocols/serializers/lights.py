from .registry import class_name
from .utils import getReferenceId


def lightTypeToString(value):
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


def lightSerializer(parent, instance, objId, context, depth):
    return {
        "parent": getReferenceId(parent),
        "id": objId,
        "type": class_name(instance),
        "properties": {
            # 'specularColor': instance.GetSpecularColor(),
            # 'ambientColor': instance.GetAmbientColor(),
            "switch": instance.GetSwitch(),
            "intensity": instance.GetIntensity(),
            "color": instance.GetDiffuseColor(),
            "position": instance.GetPosition(),
            "focalPoint": instance.GetFocalPoint(),
            "positional": instance.GetPositional(),
            "exponent": instance.GetExponent(),
            "coneAngle": instance.GetConeAngle(),
            "attenuationValues": instance.GetAttenuationValues(),
            "lightType": lightTypeToString(instance.GetLightType()),
            "shadowAttenuation": instance.GetShadowAttenuation(),
        },
    }
