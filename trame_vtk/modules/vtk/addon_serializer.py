from vtkmodules.web import render_window_serializer
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter


def rgb_float_to_hex(r, g, b):
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


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
                "fontColor": rgb_float_to_hex(*actor.GetTitleTextProperty().GetColor()),
                "fontStyle": "normal",
                "fontSize": 18,
                "fontFamily": "serif",
            },
            "tickLabelPixelOffset": 14.0,
            "tickTextStyle": {
                "fontColor": rgb_float_to_hex(*actor.GetTitleTextProperty().GetColor()),
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


def cubeAxesSerializer(parent, actor, actorId, context, depth):
    """
    Possible add-on properties for vtk.js:
        gridLines: True,
        axisLabels: None,
        axisTitlePixelOffset: 35.0,
        axisTextStyle: {
            fontColor: 'white',
            fontStyle: 'normal',
            fontSize: 18,
            fontFamily: 'serif',
        },
        tickLabelPixelOffset: 12.0,
        tickTextStyle: {
            fontColor: 'white',
            fontStyle: 'normal',
            fontSize: 14,
            fontFamily: 'serif',
        },
    """
    axisLabels = ["", "", ""]
    if actor.GetXAxisLabelVisibility():
        axisLabels[0] = actor.GetXTitle()
    if actor.GetYAxisLabelVisibility():
        axisLabels[1] = actor.GetYTitle()
    if actor.GetZAxisLabelVisibility():
        axisLabels[2] = actor.GetZTitle()

    text_color = rgb_float_to_hex(*actor.GetXAxesGridlinesProperty().GetColor())

    dependencies = []
    calls = [
        [
            "setCamera",
            [
                render_window_serializer.wrapId(
                    render_window_serializer.getReferenceId(actor.GetCamera())
                )
            ],
        ]
    ]

    prop = None
    if hasattr(actor, "GetXAxesLinesProperty"):
        prop = actor.GetXAxesLinesProperty()
    else:
        render_window_serializer.logger.debug(
            "This actor does not have a GetXAxesLinesProperty method"
        )

    if prop:
        propId = render_window_serializer.getReferenceId(prop)
        propertyInstance = render_window_serializer.serializeInstance(
            actor, prop, propId, context, depth + 1
        )
        if propertyInstance:
            dependencies.append(propertyInstance)
            calls.append(["setProperty", [render_window_serializer.wrapId(propId)]])

    return {
        "parent": render_window_serializer.getReferenceId(parent),
        "id": actorId,
        "type": "vtkCubeAxesActor",
        "properties": {
            # vtkProp
            "visibility": actor.GetVisibility(),
            "pickable": actor.GetPickable(),
            "dragable": actor.GetDragable(),
            "useBounds": actor.GetUseBounds(),
            # vtkProp3D
            "origin": actor.GetOrigin(),
            "position": actor.GetPosition(),
            "scale": actor.GetScale(),
            # vtkActor
            "forceOpaque": actor.GetForceOpaque(),
            "forceTranslucent": actor.GetForceTranslucent(),
            # vtkCubeAxesActor
            "dataBounds": actor.GetBounds(),
            "faceVisibilityAngle": 8,
            "gridLines": True,
            "axisLabels": axisLabels,
            "axisTitlePixelOffset": 35.0,
            "axisTextStyle": {
                "fontColor": text_color,
                "fontStyle": "normal",
                "fontSize": 18,
                "fontFamily": "serif",
            },
            "tickLabelPixelOffset": 12.0,
            "tickTextStyle": {
                "fontColor": text_color,
                "fontStyle": "normal",
                "fontSize": 14,
                "fontFamily": "serif",
            },
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
    setattr(render_window_serializer, "cubeAxesSerializer", cubeAxesSerializer)

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
    render_window_serializer.registerInstanceSerializer(
        "vtkCubeAxesActor", cubeAxesSerializer
    )
