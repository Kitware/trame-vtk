import logging

from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

from .registry import class_name
from .serialize import serialize
from .utils import reference_id, wrap_id
from .cache import cache_properties

logger = logging.getLogger(__name__)


def generic_mapper_serializer(parent, mapper, mapper_id, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    data_object = None
    data_object_instance = None
    lookup_table_instance = None
    calls = []
    dependencies = []

    if hasattr(mapper, "GetInputDataObject"):
        mapper.GetInputAlgorithm().Update()
        data_object = mapper.GetInputDataObject(0, 0)
    else:
        if context.debug_all:
            print("This mapper does not have GetInputDataObject method")

    if data_object:
        if data_object.IsA("vtkDataSet"):
            alg = vtkDataSetSurfaceFilter()
            alg.SetInputData(data_object)
            alg.Update()
            data_object = alg.GetOutput()

        data_object_id = "%s-dataset" % mapper_id
        data_object_instance = serialize(
            mapper, data_object, data_object_id, context, depth + 1
        )

        if data_object_instance:
            dependencies.append(data_object_instance)
            calls.append(["setInputData", [wrap_id(data_object_id)]])

    lookup_table = None

    if hasattr(mapper, "GetLookupTable"):
        lookup_table = mapper.GetLookupTable()
    else:
        if context.debug_all:
            print("This mapper does not have GetLookupTable method")

    if lookup_table:
        lookup_table_id = reference_id(lookup_table)
        lookup_table_instance = serialize(
            mapper, lookup_table, lookup_table_id, context, depth + 1
        )
        if lookup_table_instance:
            dependencies.append(lookup_table_instance)
            calls.append(["setLookupTable", [wrap_id(lookup_table_id)]])

    if data_object_instance:
        color_array_name = (
            mapper.GetArrayName()
            if mapper.GetArrayAccessMode() == 1
            else mapper.GetArrayId()
        )
        return {
            "parent": reference_id(parent),
            "id": mapper_id,
            "type": class_name(mapper),
            "properties": cache_properties(
                mapper_id,
                context,
                {
                    "resolveCoincidentTopology": mapper.GetResolveCoincidentTopology(),
                    "renderTime": mapper.GetRenderTime(),
                    "arrayAccessMode": mapper.GetArrayAccessMode(),
                    "scalarRange": mapper.GetScalarRange(),
                    "useLookupTableScalarRange": 1
                    if mapper.GetUseLookupTableScalarRange()
                    else 0,
                    "scalarVisibility": mapper.GetScalarVisibility(),
                    "colorByArrayName": color_array_name,
                    "colorMode": mapper.GetColorMode(),
                    "scalarMode": mapper.GetScalarMode(),
                    "interpolateScalarsBeforeMapping": 1
                    if mapper.GetInterpolateScalarsBeforeMapping()
                    else 0,
                },
            ),
            "calls": calls,
            "dependencies": dependencies,
        }

    return None


# -----------------------------------------------------------------------------


def generic_volume_mapper_serializer(parent, mapper, mapper_id, context, depth):
    # This kind of mapper requires us to get 2 items: input data and lookup
    # table
    data_object = None
    data_object_instance = None
    # lookup_table_instance = None
    calls = []
    dependencies = []

    if hasattr(mapper, "GetInputDataObject"):
        mapper.GetInputAlgorithm().Update()
        data_object = mapper.GetInputDataObject(0, 0)
    else:
        logger.debug("This mapper does not have GetInputDataObject method")

    if data_object:
        data_object_id = "%s-dataset" % mapper_id
        data_object_instance = serialize(
            mapper, data_object, data_object_id, context, depth + 1
        )

        if data_object_instance:
            dependencies.append(data_object_instance)
            calls.append(["setInputData", [wrap_id(data_object_id)]])

    if data_object_instance:
        if hasattr(mapper, "GetImageSampleDistance"):
            image_sample_distance = mapper.GetImageSampleDistance()
        else:
            image_sample_distance = 1.0
        return {
            "parent": reference_id(parent),
            "id": mapper_id,
            "type": class_name(mapper),
            "properties": cache_properties(
                mapper_id,
                context,
                {
                    # VolumeMapper
                    "sampleDistance": mapper.GetSampleDistance(),
                    "imageSampleDistance": image_sample_distance,
                    # "maximumSamplesPerRay": mapper.GetMaximumSamplesPerRay(),
                    "autoAdjustSampleDistances": mapper.GetAutoAdjustSampleDistances(),
                    "blendMode": mapper.GetBlendMode(),
                    # "ipScalarRange": mapper.GetIpScalarRange(),
                    # "filterMode": mapper.GetFilterMode(),
                    # "preferSizeOverAccuracy": mapper.Get(),
                },
            ),
            "calls": calls,
            "dependencies": dependencies,
        }

    return None
