import logging

from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

from .registry import class_name
from .serialize import serialize
from .utils import getReferenceId, wrapId

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def genericMapperSerializer(parent, mapper, mapperId, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    dataObject = None
    dataObjectInstance = None
    lookupTableInstance = None
    calls = []
    dependencies = []

    if hasattr(mapper, "GetInputDataObject"):
        mapper.GetInputAlgorithm().Update()
        dataObject = mapper.GetInputDataObject(0, 0)
    else:
        if context.debugAll:
            print("This mapper does not have GetInputDataObject method")

    if dataObject:
        if dataObject.IsA("vtkDataSet"):
            alg = vtkDataSetSurfaceFilter()
            alg.SetInputData(dataObject)
            alg.Update()
            dataObject = alg.GetOutput()

        dataObjectId = "%s-dataset" % mapperId
        dataObjectInstance = serialize(
            mapper, dataObject, dataObjectId, context, depth + 1
        )

        if dataObjectInstance:
            dependencies.append(dataObjectInstance)
            calls.append(["setInputData", [wrapId(dataObjectId)]])

    lookupTable = None

    if hasattr(mapper, "GetLookupTable"):
        lookupTable = mapper.GetLookupTable()
    else:
        if context.debugAll:
            print("This mapper does not have GetLookupTable method")

    if lookupTable:
        lookupTableId = getReferenceId(lookupTable)
        lookupTableInstance = serialize(
            mapper, lookupTable, lookupTableId, context, depth + 1
        )
        if lookupTableInstance:
            dependencies.append(lookupTableInstance)
            calls.append(["setLookupTable", [wrapId(lookupTableId)]])

    if dataObjectInstance:
        colorArrayName = (
            mapper.GetArrayName()
            if mapper.GetArrayAccessMode() == 1
            else mapper.GetArrayId()
        )
        return {
            "parent": getReferenceId(parent),
            "id": mapperId,
            "type": class_name(mapper),
            "properties": {
                "resolveCoincidentTopology": mapper.GetResolveCoincidentTopology(),
                "renderTime": mapper.GetRenderTime(),
                "arrayAccessMode": mapper.GetArrayAccessMode(),
                "scalarRange": mapper.GetScalarRange(),
                "useLookupTableScalarRange": 1
                if mapper.GetUseLookupTableScalarRange()
                else 0,
                "scalarVisibility": mapper.GetScalarVisibility(),
                "colorByArrayName": colorArrayName,
                "colorMode": mapper.GetColorMode(),
                "scalarMode": mapper.GetScalarMode(),
                "interpolateScalarsBeforeMapping": 1
                if mapper.GetInterpolateScalarsBeforeMapping()
                else 0,
            },
            "calls": calls,
            "dependencies": dependencies,
        }

    return None


# -----------------------------------------------------------------------------


def genericVolumeMapperSerializer(parent, mapper, mapperId, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    dataObject = None
    dataObjectInstance = None
    # lookupTableInstance = None
    calls = []
    dependencies = []

    if hasattr(mapper, "GetInputDataObject"):
        mapper.GetInputAlgorithm().Update()
        dataObject = mapper.GetInputDataObject(0, 0)
    else:
        logger.debug("This mapper does not have GetInputDataObject method")

    if dataObject:
        dataObjectId = "%s-dataset" % mapperId
        dataObjectInstance = serialize(
            mapper, dataObject, dataObjectId, context, depth + 1
        )

        if dataObjectInstance:
            dependencies.append(dataObjectInstance)
            calls.append(["setInputData", [wrapId(dataObjectId)]])

    if dataObjectInstance:
        if hasattr(mapper, "GetImageSampleDistance"):
            imageSampleDistance = mapper.GetImageSampleDistance()
        else:
            imageSampleDistance = 1.0
        return {
            "parent": getReferenceId(parent),
            "id": mapperId,
            "type": class_name(mapper),
            "properties": {
                # VolumeMapper
                "sampleDistance": mapper.GetSampleDistance(),
                "imageSampleDistance": imageSampleDistance,
                # "maximumSamplesPerRay": mapper.GetMaximumSamplesPerRay(),
                "autoAdjustSampleDistances": mapper.GetAutoAdjustSampleDistances(),
                "blendMode": mapper.GetBlendMode(),
                # "ipScalarRange": mapper.GetIpScalarRange(),
                # "filterMode": mapper.GetFilterMode(),
                # "preferSizeOverAccuracy": mapper.Get(),
            },
            "calls": calls,
            "dependencies": dependencies,
        }

    return None
