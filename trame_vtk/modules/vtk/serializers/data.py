import logging

from vtkmodules.vtkFiltersGeometry import vtkCompositeDataGeometryFilter
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

from .helpers import extractRequiredFields, getArrayDescription
from .registry import class_name
from .serialize import serialize
from .utils import getReferenceId, wrapId

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def polydataSerializer(
    parent, dataset, datasetId, context, depth, requested_fields=["Normals", "TCoords"]
):
    if dataset and dataset.GetPoints():
        properties = {}

        # Points
        points = getArrayDescription(dataset.GetPoints().GetData(), context)
        points["vtkClass"] = "vtkPoints"
        properties["points"] = points

        # Verts
        if dataset.GetVerts() and dataset.GetVerts().GetData().GetNumberOfTuples() > 0:
            _verts = getArrayDescription(dataset.GetVerts().GetData(), context)
            properties["verts"] = _verts
            properties["verts"]["vtkClass"] = "vtkCellArray"

        # Lines
        if dataset.GetLines() and dataset.GetLines().GetData().GetNumberOfTuples() > 0:
            _lines = getArrayDescription(dataset.GetLines().GetData(), context)
            properties["lines"] = _lines
            properties["lines"]["vtkClass"] = "vtkCellArray"

        # Polys
        if dataset.GetPolys() and dataset.GetPolys().GetData().GetNumberOfTuples() > 0:
            _polys = getArrayDescription(dataset.GetPolys().GetData(), context)
            properties["polys"] = _polys
            properties["polys"]["vtkClass"] = "vtkCellArray"

        # Strips
        if (
            dataset.GetStrips()
            and dataset.GetStrips().GetData().GetNumberOfTuples() > 0
        ):
            _strips = getArrayDescription(dataset.GetStrips().GetData(), context)
            properties["strips"] = _strips
            properties["strips"]["vtkClass"] = "vtkCellArray"

        # Fields
        properties["fields"] = []
        extractRequiredFields(
            properties["fields"], parent, dataset, context, requested_fields
        )

        return {
            "parent": getReferenceId(parent),
            "id": datasetId,
            "type": class_name(dataset),
            "properties": properties,
        }

    logger.debug("This dataset has no points!")
    return None


# -----------------------------------------------------------------------------


def mergeToPolydataSerializer(
    parent,
    dataObject,
    dataObjectId,
    context,
    depth,
    requested_fields=["Normals", "TCoords"],
):
    dataset = None

    if dataObject.IsA("vtkCompositeDataSet"):
        gf = vtkCompositeDataGeometryFilter()
        gf.SetInputData(dataObject)
        gf.Update()
        dataset = gf.GetOutput()
    elif dataObject.IsA("vtkUnstructuredGrid"):
        gf = vtkDataSetSurfaceFilter()
        gf.SetInputData(dataObject)
        gf.Update()
        dataset = gf.GetOutput()
    else:
        # FIXME: how are we supposed to get 'mapper' here?
        # dataset = mapper.GetInput()
        dataset = None

    return polydataSerializer(
        parent, dataset, dataObjectId, context, depth, requested_fields
    )


# -----------------------------------------------------------------------------


def imagedataSerializer(
    parent, dataset, datasetId, context, depth, requested_fields=["Normals", "TCoords"]
):
    if hasattr(dataset, "GetDirectionMatrix"):
        direction = [dataset.GetDirectionMatrix().GetElement(0, i) for i in range(9)]
    else:
        direction = [1, 0, 0, 0, 1, 0, 0, 0, 1]

    # Extract dataset fields
    fields = []
    extractRequiredFields(fields, parent, dataset, context, "*")

    return {
        "parent": getReferenceId(parent),
        "id": datasetId,
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


def genericVolumeSerializer(parent, actor, actorId, context, depth):
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
            },
            "calls": calls,
            "dependencies": dependencies,
        }

    return None
