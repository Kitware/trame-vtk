from vtkmodules.web import render_window_serializer


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
            colorMode = mapper.GetColorMode()
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
                arrayMeta = render_window_serializer.getArrayDescription(array, context)
                if arrayMeta:
                    arrayMeta["location"] = location
                    attribute = field_data.IsArrayAnAttribute(array_index)
                    arrayMeta["registration"] = (
                        "set" + field_data.GetAttributeTypeAsString(attribute)
                        if attribute >= 0
                        else "addArray"
                    )
                    extractedFields.append(arrayMeta)


def registerAddOnSerializers():
    # Override extractRequiredFields to fix handling of Normals/TCoords
    setattr(render_window_serializer, "extractRequiredFields", extractRequiredFields)
