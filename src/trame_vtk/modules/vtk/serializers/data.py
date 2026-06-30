import importlib
import logging
import os
import sys

vtk_module_name = os.environ.get("VTK_MODULE_NAME", "vtkmodules")
sys.modules["vtk_module"] = importlib.import_module(vtk_module_name)

from vtk_module.vtkFiltersGeometry import (  # noqa: E402
    vtkCompositeDataGeometryFilter,
    vtkDataSetSurfaceFilter,
)
from vtkmodules.vtkCommonCore import vtkIdTypeArray  # noqa: E402

from .helpers import extract_required_fields, get_array_description  # noqa: E402
from .registry import class_name  # noqa: E402
from .serialize import serialize  # noqa: E402
from .utils import get_js_array_type, reference_id, wrap_id  # noqa: E402

logger = logging.getLogger(__name__)


def polydata_serializer(
    parent,
    dataset,
    dataset_id,
    context,
    _depth,
    requested_fields=None,
):
    if requested_fields is None:
        requested_fields = ["Normals", "TCoords"]
    if dataset and dataset.GetPoints():
        properties = {}

        # Points
        # Handle coordinate conversion if needed
        convert = {}
        js_point_types = get_js_array_type(dataset.GetPoints().GetData())
        if js_point_types not in ["Float32Array", "Float64Array"]:
            convert["dataType"] = (
                "Float32Array" if "32" in js_point_types else "Float64Array"
            )

        points = get_array_description(
            dataset.GetPoints().GetData(), context, **convert
        )
        points["vtkClass"] = "vtkPoints"
        properties["points"] = points

        # Cells
        for key, cells in [
            ("verts", dataset.GetVerts()),
            ("lines", dataset.GetLines()),
            ("polys", dataset.GetPolys()),
            ("strips", dataset.GetStrips()),
        ]:
            if not cells or cells.GetNumberOfCells() == 0:
                continue

            cell_array = None
            if hasattr(cells, "ExportLegacyFormat"):
                cell_array = vtkIdTypeArray()
                cells.ExportLegacyFormat(cell_array)
            else:
                cell_array = cells.GetData()

            properties[key] = get_array_description(cell_array, context)
            properties[key]["vtkClass"] = "vtkCellArray"

        # Fields
        properties["fields"] = []
        extract_required_fields(
            properties["fields"], parent, dataset, context, requested_fields
        )

        return {
            "parent": reference_id(parent),
            "id": dataset_id,
            "type": class_name(dataset),
            "properties": properties,
        }

    logger.debug("This dataset has no points!")
    return None


# -----------------------------------------------------------------------------


def merge_to_polydata_serializer(
    parent,
    data_object,
    data_object_id,
    context,
    depth,
    requested_fields=None,
):
    if requested_fields is None:
        requested_fields = ["Normals", "TCoords"]
    dataset = None

    if data_object.IsA("vtkCompositeDataSet"):
        gf = vtkCompositeDataGeometryFilter()
        gf.SetInputData(data_object)
        gf.Update()
        dataset = gf.GetOutput()
    elif data_object.IsA("vtkUnstructuredGrid"):
        gf = vtkDataSetSurfaceFilter()
        gf.SetInputData(data_object)
        gf.Update()
        dataset = gf.GetOutput()
    else:
        # FIXME: how are we supposed to get 'mapper' here?
        # dataset = mapper.GetInput()
        dataset = None

    return polydata_serializer(
        parent, dataset, data_object_id, context, depth, requested_fields
    )


# -----------------------------------------------------------------------------


def imagedata_serializer(
    parent,
    dataset,
    dataset_id,
    context,
    _depth,
    requested_fields=None,  # noqa: ARG001
):
    if hasattr(dataset, "GetDirectionMatrix"):
        direction = [dataset.GetDirectionMatrix().GetElement(0, i) for i in range(9)]
    else:
        direction = [1, 0, 0, 0, 1, 0, 0, 0, 1]

    # Extract dataset fields
    fields = []
    extract_required_fields(fields, parent, dataset, context, "*")

    return {
        "parent": reference_id(parent),
        "id": dataset_id,
        "type": class_name(dataset),
        "properties": {
            "spacing": dataset.GetSpacing(),
            "origin": dataset.GetOrigin(),
            "extent": dataset.GetExtent(),
            "direction": direction,
            "fields": fields,
        },
    }


# -----------------------------------------------------------------------------


def generic_volume_serializer(parent, actor, actor_id, context, depth):
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
            "properties": {
                # vtkProp
                "visibility": actor_visibility,
                "pickable": actor.GetPickable(),
                "dragable": actor.GetDragable(),
                "useBounds": actor.GetUseBounds(),
                # vtkProp3D
                "origin": actor.GetOrigin(),
                "position": actor.GetPosition(),
                "scale": actor.GetScale(),
                # additional properties
                **add_on,
            },
            "calls": calls,
            "dependencies": dependencies,
        }

    return None
