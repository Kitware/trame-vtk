from .registry import class_name
from .serialize import serialize
from .utils import reference_id, wrap_id


def renderer_serializer(parent, instance, obj_id, context, depth):
    dependencies = []
    view_prop_ids = []
    lights_ids = []
    calls = []

    # Camera
    camera = instance.GetActiveCamera()
    camera_id = reference_id(camera)
    camera_instance = serialize(instance, camera, camera_id, context, depth + 1)
    if camera_instance:
        dependencies.append(camera_instance)
        calls.append(["setActiveCamera", [wrap_id(camera_id)]])

    # View prop as representation containers
    view_prop_collection = instance.GetViewProps()
    for rp_idx in range(view_prop_collection.GetNumberOfItems()):
        view_prop = view_prop_collection.GetItemAsObject(rp_idx)
        view_prop_id = reference_id(view_prop)

        view_prop_instance = serialize(
            instance, view_prop, view_prop_id, context, depth + 1
        )
        if view_prop_instance:
            dependencies.append(view_prop_instance)
            view_prop_ids.append(view_prop_id)

    calls += context.build_dependency_call_list(
        "%s-props" % obj_id, view_prop_ids, "addViewProp", "removeViewProp"
    )

    # Lights
    light_collection = instance.GetLights()
    for light_idx in range(light_collection.GetNumberOfItems()):
        light = light_collection.GetItemAsObject(light_idx)
        light_id = reference_id(light)

        light_instance = serialize(instance, light, light_id, context, depth + 1)
        if light_instance:
            dependencies.append(light_instance)
            lights_ids.append(light_id)

    calls += context.build_dependency_call_list(
        "%s-lights" % obj_id, lights_ids, "addLight", "removeLight"
    )

    if len(dependencies) > 1:
        return {
            "parent": reference_id(parent),
            "id": obj_id,
            "type": class_name(instance),
            "properties": {
                "background": instance.GetBackground(),
                "background2": instance.GetBackground2(),
                "viewport": instance.GetViewport(),
                # These commented properties do not yet have real setters in vtk.js
                # 'gradient_background': instance.GetGradientBackground(),
                # 'aspect': instance.GetAspect(),
                # 'pixel_aspect': instance.GetPixelAspect(),
                # 'ambient': instance.GetAmbient(),
                "twoSidedLighting": instance.GetTwoSidedLighting(),
                "lightFollowCamera": instance.GetLightFollowCamera(),
                "layer": instance.GetLayer(),
                "preserveColorBuffer": instance.GetPreserveColorBuffer(),
                "preserveDepthBuffer": instance.GetPreserveDepthBuffer(),
                "nearClippingPlaneTolerance": instance.GetNearClippingPlaneTolerance(),
                "clippingRangeExpansion": instance.GetClippingRangeExpansion(),
                "useShadows": instance.GetUseShadows(),
                "useDepthPeeling": instance.GetUseDepthPeeling(),
                "occlusionRatio": instance.GetOcclusionRatio(),
                "maximumNumberOfPeels": instance.GetMaximumNumberOfPeels(),
                "interactive": instance.GetInteractive(),
            },
            "dependencies": dependencies,
            "calls": calls,
        }

    return None


# -----------------------------------------------------------------------------


def camera_serializer(parent, instance, obj_id, context, depth):
    return {
        "parent": reference_id(parent),
        "id": obj_id,
        "type": class_name(instance),
        "properties": {
            "focalPoint": instance.GetFocalPoint(),
            "position": instance.GetPosition(),
            "viewUp": instance.GetViewUp(),
            "clippingRange": instance.GetClippingRange(),
        },
    }


# -----------------------------------------------------------------------------


def render_window_serializer(parent, instance, obj_id, context, depth):
    dependencies = []
    renderer_ids = []

    renderer_collection = instance.GetRenderers()
    for r_idx in range(renderer_collection.GetNumberOfItems()):
        # Grab the next vtkRenderer
        renderer = renderer_collection.GetItemAsObject(r_idx)
        renderer_id = reference_id(renderer)
        renderer_instance = serialize(
            instance, renderer, renderer_id, context, depth + 1
        )
        if renderer_instance:
            dependencies.append(renderer_instance)
            renderer_ids.append(renderer_id)

    calls = context.build_dependency_call_list(
        obj_id, renderer_ids, "addRenderer", "removeRenderer"
    )

    return {
        "parent": reference_id(parent),
        "id": obj_id,
        "type": class_name(instance),
        "properties": {"numberOfLayers": instance.GetNumberOfLayers()},
        "dependencies": dependencies,
        "calls": calls,
        "mtime": instance.GetMTime(),
    }
