import io
import struct
import time

from .utils import array_types_mapping, get_js_array_type, reference_id, hash_data_array


# -----------------------------------------------------------------------------
# Array helpers
# -----------------------------------------------------------------------------


def data_table_to_list(data_table):
    data_type = array_types_mapping[data_table.GetDataType()]
    element_size = struct.calcsize(data_type)
    nb_values = data_table.GetNumberOfValues()
    nb_components = data_table.GetNumberOfComponents()
    nbytes = element_size * nb_values
    if data_type != " ":
        with io.BytesIO(memoryview(data_table)) as stream:
            data = list(struct.unpack(data_type * nb_values, stream.read(nbytes)))
        return [
            data[idx * nb_components : (idx + 1) * nb_components]
            for idx in range(nb_values // nb_components)
        ]

    return None


# -----------------------------------------------------------------------------


def linspace(start, stop, num):
    delta = (stop - start) / (num - 1)
    return [start + i * delta for i in range(num)]


data_array_sha_mapping = {}


def digest(array):
    obj_id = reference_id(array)

    record = None
    if obj_id in data_array_sha_mapping:
        record = data_array_sha_mapping[obj_id]

    if record and record["mtime"] == array.GetMTime():
        return record["sha"]

    record = {"sha": hash_data_array(array), "mtime": array.GetMTime()}

    data_array_sha_mapping[obj_id] = record
    return record["sha"]


# -----------------------------------------------------------------------------


def get_range_info(array, component):
    r = array.GetRange(component)
    comp_range = {}
    comp_range["min"] = r[0]
    comp_range["max"] = r[1]
    comp_range["component"] = array.GetComponentName(component)
    return comp_range


# -----------------------------------------------------------------------------


def get_array_description(array, context, **kwargs):
    if not array:
        return None

    p_md5 = digest(array)
    context.cache_data_array(
        p_md5, {"array": array, "mTime": array.GetMTime(), "ts": time.time(), **kwargs}
    )

    root = {}
    root["hash"] = p_md5
    root["vtkClass"] = "vtkDataArray"
    root["name"] = array.GetName()
    root["dataType"] = kwargs.get("dataType", get_js_array_type(array))
    root["numberOfComponents"] = array.GetNumberOfComponents()
    root["size"] = array.GetNumberOfComponents() * array.GetNumberOfTuples()
    root["ranges"] = []
    if root["numberOfComponents"] > 1:
        for i in range(root["numberOfComponents"]):
            root["ranges"].append(get_range_info(array, i))
        root["ranges"].append(get_range_info(array, -1))
    else:
        root["ranges"].append(get_range_info(array, 0))

    return root


# -----------------------------------------------------------------------------


def extract_required_fields(
    extracted_fields, parent, dataset, context, requested_fields=["Normals", "TCoords"]
):
    arrays_to_export = set()
    export_all = "*" in requested_fields
    # Identify arrays to export
    if not export_all:
        # FIXME should evolve and support funky mapper which leverage many arrays
        if parent and parent.IsA("vtkMapper"):
            mapper = parent
            scalar_visibility = mapper.GetScalarVisibility()
            array_access_mode = mapper.GetArrayAccessMode()
            color_array_name = (
                mapper.GetArrayName() if array_access_mode == 1 else mapper.GetArrayId()
            )
            # color_mode = mapper.GetColorMode()
            scalar_mode = mapper.GetScalarMode()
            if scalar_visibility and scalar_mode in (1, 3):
                array_to_export = dataset.GetPointData().GetArray(color_array_name)
                if array_to_export is None:
                    array_to_export = dataset.GetPointData().GetScalars()
                arrays_to_export.add(array_to_export)
            if scalar_visibility and scalar_mode in (2, 4):
                array_to_export = dataset.GetCellData().GetArray(color_array_name)
                if array_to_export is None:
                    array_to_export = dataset.GetCellData().GetScalars()
                arrays_to_export.add(array_to_export)
            if scalar_visibility and scalar_mode == 0:
                array_to_export = dataset.GetPointData().GetScalars()
                if array_to_export is None:
                    array_to_export = dataset.GetCellData().GetScalars()
                arrays_to_export.add(array_to_export)

        if parent and parent.IsA("vtkTexture") and dataset.GetPointData().GetScalars():
            arrays_to_export.add(dataset.GetPointData().GetScalars())

        arrays_to_export.update(
            [
                getattr(dataset.GetPointData(), "Get" + requested_field, lambda: None)()
                for requested_field in requested_fields
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
                array_meta = get_array_description(array, context)
                if array_meta:
                    array_meta["location"] = location
                    attribute = field_data.IsArrayAnAttribute(array_index)
                    array_meta["registration"] = (
                        "set" + field_data.GetAttributeTypeAsString(attribute)
                        if attribute >= 0
                        else "addArray"
                    )
                    extracted_fields.append(array_meta)
