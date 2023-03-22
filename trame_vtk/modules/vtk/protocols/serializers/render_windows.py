from .registry import class_name
from .serialize import serialize
from .utils import getReferenceId, wrapId


def rendererSerializer(parent, instance, objId, context, depth):
    dependencies = []
    viewPropIds = []
    lightsIds = []
    calls = []

    # Camera
    camera = instance.GetActiveCamera()
    cameraId = getReferenceId(camera)
    cameraInstance = serialize(instance, camera, cameraId, context, depth + 1)
    if cameraInstance:
        dependencies.append(cameraInstance)
        calls.append(["setActiveCamera", [wrapId(cameraId)]])

    # View prop as representation containers
    viewPropCollection = instance.GetViewProps()
    for rpIdx in range(viewPropCollection.GetNumberOfItems()):
        viewProp = viewPropCollection.GetItemAsObject(rpIdx)
        viewPropId = getReferenceId(viewProp)

        viewPropInstance = serialize(instance, viewProp, viewPropId, context, depth + 1)
        if viewPropInstance:
            dependencies.append(viewPropInstance)
            viewPropIds.append(viewPropId)

    calls += context.buildDependencyCallList(
        "%s-props" % objId, viewPropIds, "addViewProp", "removeViewProp"
    )

    # Lights
    lightCollection = instance.GetLights()
    for lightIdx in range(lightCollection.GetNumberOfItems()):
        light = lightCollection.GetItemAsObject(lightIdx)
        lightId = getReferenceId(light)

        lightInstance = serialize(instance, light, lightId, context, depth + 1)
        if lightInstance:
            dependencies.append(lightInstance)
            lightsIds.append(lightId)

    calls += context.buildDependencyCallList(
        "%s-lights" % objId, lightsIds, "addLight", "removeLight"
    )

    if len(dependencies) > 1:
        return {
            "parent": getReferenceId(parent),
            "id": objId,
            "type": class_name(instance),
            "properties": {
                "background": instance.GetBackground(),
                "background2": instance.GetBackground2(),
                "viewport": instance.GetViewport(),
                # These commented properties do not yet have real setters in vtk.js
                # 'gradientBackground': instance.GetGradientBackground(),
                # 'aspect': instance.GetAspect(),
                # 'pixelAspect': instance.GetPixelAspect(),
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


def cameraSerializer(parent, instance, objId, context, depth):
    return {
        "parent": getReferenceId(parent),
        "id": objId,
        "type": class_name(instance),
        "properties": {
            "focalPoint": instance.GetFocalPoint(),
            "position": instance.GetPosition(),
            "viewUp": instance.GetViewUp(),
            "clippingRange": instance.GetClippingRange(),
        },
    }


# -----------------------------------------------------------------------------


def renderWindowSerializer(parent, instance, objId, context, depth):
    dependencies = []
    rendererIds = []

    rendererCollection = instance.GetRenderers()
    for rIdx in range(rendererCollection.GetNumberOfItems()):
        # Grab the next vtkRenderer
        renderer = rendererCollection.GetItemAsObject(rIdx)
        rendererId = getReferenceId(renderer)
        rendererInstance = serialize(instance, renderer, rendererId, context, depth + 1)
        if rendererInstance:
            dependencies.append(rendererInstance)
            rendererIds.append(rendererId)

    calls = context.buildDependencyCallList(
        objId, rendererIds, "addRenderer", "removeRenderer"
    )

    return {
        "parent": getReferenceId(parent),
        "id": objId,
        "type": class_name(instance),
        "properties": {"numberOfLayers": instance.GetNumberOfLayers()},
        "dependencies": dependencies,
        "calls": calls,
        "mtime": instance.GetMTime(),
    }
