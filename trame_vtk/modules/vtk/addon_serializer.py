from vtkmodules import web
from vtkmodules.web import render_window_serializer
from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter
from vtkmodules.vtkCommonMath import vtkMatrix4x4
from vtkmodules.vtkRenderingCore import vtkColorTransferFunction

# Patch support for BigInt64 (VTK_LONG_LONG)
# This requires the latest VTK.js
if len(web.arrayTypesMapping) == 16:
    # Mapping is done by index of the list
    web.arrayTypesMapping.append("ll")  # VTK_LONG_LONG            16
    web.arrayTypesMapping.append("LL")  # VTK_UNSIGNED_LONG_LONG   17
    web.javascriptMapping["ll"] = "BigInt64Array"
    web.javascriptMapping["LL"] = "BigUint64Array"


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
        "parent": render_window_serializer.getReferenceId(parent),
        "id": datasetId,
        "type": render_window_serializer.class_name(dataset),
        "properties": {
            "spacing": dataset.GetSpacing(),
            "origin": dataset.GetOrigin(),
            "extent": dataset.GetExtent(),
            "direction": direction,
            "fields": fields,
        },
    }


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
        render_window_serializer.logger.debug(
            "This mapper does not have GetInputDataObject method"
        )

    if dataObject:
        dataObjectId = "%s-dataset" % mapperId
        dataObjectInstance = render_window_serializer.serializeInstance(
            mapper, dataObject, dataObjectId, context, depth + 1
        )

        if dataObjectInstance:
            dependencies.append(dataObjectInstance)
            calls.append(
                ["setInputData", [render_window_serializer.wrapId(dataObjectId)]]
            )

    if dataObjectInstance:
        if hasattr(mapper, "GetImageSampleDistance"):
            imageSampleDistance = mapper.GetImageSampleDistance()
        else:
            imageSampleDistance = 1.0
        return {
            "parent": render_window_serializer.getReferenceId(parent),
            "id": mapperId,
            "type": render_window_serializer.class_name(mapper),
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


def axesActorSerializer(parent, actor, actorId, context, depth):
    actorVisibility = actor.GetVisibility()

    if not actorVisibility:
        return None

    # C++ extract
    label_show = actor.GetAxisLabels()
    # label_position = actor.GetNormalizedLabelPosition()

    # shaft_length = actor.GetNormalizedShaftLength()
    shaft_type = actor.GetShaftType()  # int [line/cylinder]

    tip_length = actor.GetNormalizedTipLength()
    # tip_type = actor.GetTipType() # int [cone/sphere]

    cone_resolution = actor.GetConeResolution()
    cone_radius = actor.GetConeRadius()

    cylinder_resolution = actor.GetCylinderResolution()
    cylinder_radius = actor.GetCylinderRadius()

    # sphere_radius = actor.GetSphereRadius()
    # sphere_resolution = actor.GetSphereResolution()

    # XYZ...
    # actor.GetXAxisCaptionActor2D()
    # actor.GetXAxisTipProperty()
    # actor.GetXAxisShaftProperty()
    # actor.GetXAxisLabelText()

    # Apply transform
    user_matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    if actor.GetUserTransform():
        matrix = vtkMatrix4x4()
        actor.GetUserTransform().GetTranspose(matrix)
        for i in range(4):
            for j in range(4):
                idx = i + 4 * j
                user_matrix[idx] = matrix.GetElement(j, i)

    return {
        "parent": render_window_serializer.getReferenceId(parent),
        "id": actorId,
        "type": "vtkAxesActor",
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
            "userMatrix": user_matrix,
            # vtkAxesActor
            "labels": {
                "show": label_show,
                "x": actor.GetXAxisLabelText(),
                "y": actor.GetYAxisLabelText(),
                "z": actor.GetZAxisLabelText(),
            },
            "config": {
                "recenter": 0,
                "tipResolution": cone_resolution,  # 60,
                "tipRadius": 0.2 * cone_radius,  # 0.1,
                "tipLength": tip_length[0],  # 0.2,
                "shaftResolution": cylinder_resolution,  # 60,
                "shaftRadius": 0.01 if shaft_type else cylinder_radius,  # 0.03,
                "invert": 0,
            },
            "xAxisColor": list(
                map(lambda x: int(x * 255), actor.GetXAxisTipProperty().GetColor())
            ),
            "yAxisColor": list(
                map(lambda x: int(x * 255), actor.GetYAxisTipProperty().GetColor())
            ),
            "zAxisColor": list(
                map(lambda x: int(x * 255), actor.GetZAxisTipProperty().GetColor())
            ),
        },
    }


def colorTransferFunctionSerializer(parent, instance, objId, context, depth):
    nodes = []
    for i in range(instance.GetSize()):
        # x, r, g, b, midpoint, sharpness
        node = [0, 0, 0, 0, 0, 0]
        instance.GetNodeValue(i, node)
        nodes.append(node)

    discretize = 0
    numberOfValues = instance.GetSize()
    if hasattr(instance, "GetDiscretize"):
        discretize = (
            instance.GetDiscretize() if hasattr(instance, "GetDiscretize") else 0
        )
        numberOfValues = (
            instance.GetNumberOfValues()
            if hasattr(instance, "GetNumberOfValues")
            else 256
        )
    elif numberOfValues < 256:
        discretize = 1

    return {
        "parent": render_window_serializer.getReferenceId(parent),
        "id": objId,
        "type": render_window_serializer.class_name(instance),
        "properties": {
            "clamping": 1 if instance.GetClamping() else 0,
            "colorSpace": instance.GetColorSpace(),
            "hSVWrap": 1 if instance.GetHSVWrap() else 0,
            # 'nanColor': instance.GetNanColor(),                  # Breaks client
            # 'belowRangeColor': instance.GetBelowRangeColor(),    # Breaks client
            # 'aboveRangeColor': instance.GetAboveRangeColor(),    # Breaks client
            # 'useAboveRangeColor': 1 if instance.GetUseAboveRangeColor() else 0,
            # 'useBelowRangeColor': 1 if instance.GetUseBelowRangeColor() else 0,
            "allowDuplicateScalars": 1 if instance.GetAllowDuplicateScalars() else 0,
            "alpha": instance.GetAlpha(),
            "vectorComponent": instance.GetVectorComponent(),
            "vectorSize": instance.GetVectorSize(),
            "vectorMode": instance.GetVectorMode(),
            "indexedLookup": instance.GetIndexedLookup(),
            "nodes": nodes,
            "numberOfValues": numberOfValues,
            "discretize": discretize,
        },
    }


def lookupTableToColorTransferFunction(lookupTable):
    dataTable = lookupTable.GetTable()
    table = render_window_serializer.dataTableToList(dataTable)

    if not table:
        lookupTable.Build()
        table = render_window_serializer.dataTableToList(dataTable)

    if table:
        ctf = vtkColorTransferFunction()
        ctf.DeepCopy(lookupTable)  # <== needed to capture vector props

        tableRange = lookupTable.GetTableRange()
        points = render_window_serializer.linspace(*tableRange, num=len(table))
        for x, rgba in zip(points, table):
            ctf.AddRGBPoint(x, *[x / 255 for x in rgba[:3]])

        return ctf

    return None


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
    setattr(render_window_serializer, "imagedataSerializer", imagedataSerializer)
    setattr(
        render_window_serializer,
        "genericVolumeMapperSerializer",
        genericVolumeMapperSerializer,
    )
    setattr(
        render_window_serializer,
        "colorTransferFunctionSerializer",
        colorTransferFunctionSerializer,
    )
    setattr(
        render_window_serializer,
        "lookupTableToColorTransferFunction",
        lookupTableToColorTransferFunction,
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
    for name in [
        "vtkVolumeMapper",
        "vtkFixedPointVolumeRayCastMapper",
        "vtkGPUVolumeRayCastMapper",
        "vtkOpenGLGPUVolumeRayCastMapper",
        "vtkSmartVolumeMapper",
    ]:
        render_window_serializer.registerInstanceSerializer(
            name, genericVolumeMapperSerializer
        )

    render_window_serializer.registerInstanceSerializer(
        "vtkScalarBarActor", scalarBarActorSerializer
    )
    render_window_serializer.registerInstanceSerializer(
        "vtkCubeAxesActor", cubeAxesSerializer
    )
    render_window_serializer.registerInstanceSerializer(
        "vtkImageData", imagedataSerializer
    )
    render_window_serializer.registerInstanceSerializer(
        "vtkAxesActor", axesActorSerializer
    )
