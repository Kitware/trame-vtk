from vtkmodules.web import render_window_serializer
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter


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
        dataObjectInstance = render_window_serializer.serializeInstance(
            mapper, dataObject, dataObjectId, context, depth + 1
        )

        if dataObjectInstance:
            dependencies.append(dataObjectInstance)
            calls.append(
                ["setInputData", [render_window_serializer.wrapId(dataObjectId)]]
            )

    lookupTable = None

    if hasattr(mapper, "GetLookupTable"):
        lookupTable = mapper.GetLookupTable()
    else:
        if context.debugAll:
            print("This mapper does not have GetLookupTable method")

    if lookupTable:
        lookupTableId = render_window_serializer.getReferenceId(lookupTable)
        lookupTableInstance = render_window_serializer.serializeInstance(
            mapper, lookupTable, lookupTableId, context, depth + 1
        )
        if lookupTableInstance:
            dependencies.append(lookupTableInstance)
            calls.append(
                ["setLookupTable", [render_window_serializer.wrapId(lookupTableId)]]
            )

    if dataObjectInstance:
        colorArrayName = (
            mapper.GetArrayName()
            if mapper.GetArrayAccessMode() == 1
            else mapper.GetArrayId()
        )
        return {
            "parent": render_window_serializer.getReferenceId(parent),
            "id": mapperId,
            "type": render_window_serializer.class_name(mapper),
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


def scalarBarActorSerializer(parent, actor, actorId, context, depth):
    dependencies = []
    calls = []
    lut = actor.GetLookupTable()
    if not lut:
        return None

    lutId = render_window_serializer.getReferenceId(lut)
    lutInstance = render_window_serializer.serializeInstance(
        actor, lut, lutId, context, depth + 1
    )
    if not lutInstance:
        return None

    dependencies.append(lutInstance)
    calls.append(["setScalarsToColors", [render_window_serializer.wrapId(lutId)]])

    prop = None
    if hasattr(actor, "GetProperty"):
        prop = actor.GetProperty()
    else:
        if context.debugAll:
            print("This scalarBarActor does not have a GetProperty method")

        if prop:
            propId = render_window_serializer.getReferenceId(prop)
            propertyInstance = render_window_serializer.serializeInstance(
                actor, prop, propId, context, depth + 1
            )
            if propertyInstance:
                dependencies.append(propertyInstance)
                calls.append(["setProperty", [render_window_serializer.wrapId(propId)]])

    axisLabel = actor.GetTitle()
    width = actor.GetWidth()
    height = actor.GetHeight()

    return {
        "parent": render_window_serializer.getReferenceId(parent),
        "id": actorId,
        "type": "vtkScalarBarActor",
        "properties": {
            # vtkProp
            "visibility": actor.GetVisibility(),
            "pickable": actor.GetPickable(),
            "dragable": actor.GetDragable(),
            "useBounds": actor.GetUseBounds(),
            # vtkActor2D
            # "position": actor.GetPosition(),
            # "position2": actor.GetPosition2(),
            # "width": actor.GetWidth(),
            # "height": actor.GetHeight(),
            # vtkScalarBarActor
            "automated": True,
            "axisLabel": axisLabel,
            # 'barPosition': [0, 0],
            # 'barSize': [0, 0],
            "boxPosition": [0.88, -0.92],
            "boxSize": [width, height],
            "axisTitlePixelOffset": 36.0,
            "axisTextStyle": {
                "fontColor": actor.GetTitleTextProperty().GetColor(),
                "fontStyle": "normal",
                "fontSize": 18,
                "fontFamily": "serif",
            },
            "tickLabelPixelOffset": 14.0,
            "tickTextStyle": {
                "fontColor": actor.GetTitleTextProperty().GetColor(),
                "fontStyle": "normal",
                "fontSize": 14,
                "fontFamily": "serif",
            },
            "drawNanAnnotation": actor.GetDrawNanAnnotation(),
            "drawBelowRangeSwatch": actor.GetDrawBelowRangeSwatch(),
            "drawAboveRangeSwatch": actor.GetDrawAboveRangeSwatch(),
        },
        "calls": calls,
        "dependencies": dependencies,
    }


def registerAddOnSerializers():
    # Override extractRequiredFields to fix handling of Normals/TCoords
    setattr(render_window_serializer, "extractRequiredFields", extractRequiredFields)
    setattr(
        render_window_serializer, "genericMapperSerializer", genericMapperSerializer
    )
    setattr(
        render_window_serializer, "scalarBarActorSerializer", scalarBarActorSerializer
    )

    for name in [
        "vtkMapper",
        "vtkDataSetMapper",
        "vtkPolyDataMapper",
        "vtkImageDataMapper",
        "vtkOpenGLPolyDataMapper",
        "vtkCompositePolyDataMapper2",
    ]:
        render_window_serializer.registerInstanceSerializer(
            name, genericMapperSerializer
        )

    render_window_serializer.registerInstanceSerializer(
        "vtkScalarBarActor", scalarBarActorSerializer
    )
