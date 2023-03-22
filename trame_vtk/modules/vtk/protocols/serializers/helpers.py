import io
import struct
import time

from .utils import arrayTypesMapping, getJSArrayType, getReferenceId, hashDataArray


# -----------------------------------------------------------------------------
# Array helpers
# -----------------------------------------------------------------------------


def dataTableToList(dataTable):
    dataType = arrayTypesMapping[dataTable.GetDataType()]
    elementSize = struct.calcsize(dataType)
    nbValues = dataTable.GetNumberOfValues()
    nbComponents = dataTable.GetNumberOfComponents()
    nbytes = elementSize * nbValues
    if dataType != " ":
        with io.BytesIO(memoryview(dataTable)) as stream:
            data = list(struct.unpack(dataType * nbValues, stream.read(nbytes)))
        return [
            data[idx * nbComponents : (idx + 1) * nbComponents]
            for idx in range(nbValues // nbComponents)
        ]

    return None


# -----------------------------------------------------------------------------


def linspace(start, stop, num):
    delta = (stop - start) / (num - 1)
    return [start + i * delta for i in range(num)]


dataArrayShaMapping = {}


def digest(array):
    objId = getReferenceId(array)

    record = None
    if objId in dataArrayShaMapping:
        record = dataArrayShaMapping[objId]

    if record and record["mtime"] == array.GetMTime():
        return record["sha"]

    record = {"sha": hashDataArray(array), "mtime": array.GetMTime()}

    dataArrayShaMapping[objId] = record
    return record["sha"]


# -----------------------------------------------------------------------------


def getRangeInfo(array, component):
    r = array.GetRange(component)
    compRange = {}
    compRange["min"] = r[0]
    compRange["max"] = r[1]
    compRange["component"] = array.GetComponentName(component)
    return compRange


# -----------------------------------------------------------------------------


def getArrayDescription(array, context):
    if not array:
        return None

    pMd5 = digest(array)
    context.cacheDataArray(
        pMd5, {"array": array, "mTime": array.GetMTime(), "ts": time.time()}
    )

    root = {}
    root["hash"] = pMd5
    root["vtkClass"] = "vtkDataArray"
    root["name"] = array.GetName()
    root["dataType"] = getJSArrayType(array)
    root["numberOfComponents"] = array.GetNumberOfComponents()
    root["size"] = array.GetNumberOfComponents() * array.GetNumberOfTuples()
    root["ranges"] = []
    if root["numberOfComponents"] > 1:
        for i in range(root["numberOfComponents"]):
            root["ranges"].append(getRangeInfo(array, i))
        root["ranges"].append(getRangeInfo(array, -1))
    else:
        root["ranges"].append(getRangeInfo(array, 0))

    return root


# -----------------------------------------------------------------------------


def extractRequiredFields(
    extractedFields, parent, dataset, context, requestedFields=["Normals", "TCoords"]
):
    arrays_to_export = set()
    export_all = "*" in requestedFields
    # Identify arrays to export
    if not export_all:
        # FIXME should evolve and support funky mapper which leverage many arrays
        if parent and parent.IsA("vtkMapper"):
            mapper = parent
            scalarVisibility = mapper.GetScalarVisibility()
            arrayAccessMode = mapper.GetArrayAccessMode()
            colorArrayName = (
                mapper.GetArrayName() if arrayAccessMode == 1 else mapper.GetArrayId()
            )
            # colorMode = mapper.GetColorMode()
            scalarMode = mapper.GetScalarMode()
            if scalarVisibility and scalarMode in (1, 3):
                array_to_export = dataset.GetPointData().GetArray(colorArrayName)
                if array_to_export is None:
                    array_to_export = dataset.GetPointData().GetScalars()
                arrays_to_export.add(array_to_export)
            if scalarVisibility and scalarMode in (2, 4):
                array_to_export = dataset.GetCellData().GetArray(colorArrayName)
                if array_to_export is None:
                    array_to_export = dataset.GetCellData().GetScalars()
                arrays_to_export.add(array_to_export)
            if scalarVisibility and scalarMode == 0:
                array_to_export = dataset.GetPointData().GetScalars()
                if array_to_export is None:
                    array_to_export = dataset.GetCellData().GetScalars()
                arrays_to_export.add(array_to_export)

        if parent and parent.IsA("vtkTexture") and dataset.GetPointData().GetScalars():
            arrays_to_export.add(dataset.GetPointData().GetScalars())

        arrays_to_export.update(
            [
                getattr(dataset.GetPointData(), "Get" + requestedField, lambda: None)()
                for requestedField in requestedFields
            ]
        )

    # Browse all arrays
    for location, field_data in [
        ("pointData", dataset.GetPointData()),
        ("cellData", dataset.GetCellData()),
    ]:
        for array_index in range(field_data.GetNumberOfArrays()):
            array = field_data.GetArray(array_index)
            if export_all or array in arrays_to_export:
                arrayMeta = getArrayDescription(array, context)
                if arrayMeta:
                    arrayMeta["location"] = location
                    attribute = field_data.IsArrayAnAttribute(array_index)
                    arrayMeta["registration"] = (
                        "set" + field_data.GetAttributeTypeAsString(attribute)
                        if attribute >= 0
                        else "addArray"
                    )
                    extractedFields.append(arrayMeta)
