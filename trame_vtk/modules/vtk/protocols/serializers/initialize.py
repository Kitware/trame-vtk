import logging

from .actors import (
    axesActorSerializer,
    cubeAxesSerializer,
    genericActorSerializer,
    scalarBarActorSerializer,
)
from .data import (
    imagedataSerializer,
    genericVolumeSerializer,
    mergeToPolydataSerializer,
    polydataSerializer,
)
from .lights import lightSerializer
from .lookup_tables import (
    colorTransferFunctionSerializer,
    discretizableColorTransferFunctionSerializer,
    lookupTableSerializer2,
)
from .mappers import genericMapperSerializer, genericVolumeMapperSerializer
from .properties import propertySerializer, volumePropertySerializer
from .pwf import pwfSerializer
from .registry import registerInstanceSerializer, registerJSClass
from .render_windows import cameraSerializer, rendererSerializer, renderWindowSerializer
from .textures import textureSerializer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def initializeSerializers():
    # Define which serializer will be used for which VTK classes
    serializers = {
        # Actors/viewProps
        genericActorSerializer: [
            "vtkActor",
            "vtkOpenGLActor",
            "vtkPVLODActor",
        ],
        # Mappers
        genericMapperSerializer: [
            "vtkMapper",
            "vtkDataSetMapper",
            "vtkPolyDataMapper",
            "vtkImageDataMapper",
            "vtkOpenGLPolyDataMapper",
            "vtkCompositePolyDataMapper2",
        ],
        # Volume mappers
        genericVolumeMapperSerializer: [
            "vtkVolumeMapper",
            "vtkFixedPointVolumeRayCastMapper",
            "vtkGPUVolumeRayCastMapper",
            "vtkOpenGLGPUVolumeRayCastMapper",
            "vtkSmartVolumeMapper",
        ],
        # Volume/viewProps
        genericVolumeSerializer: "vtkVolume",
        # Textures
        textureSerializer: [
            "vtkTexture",
            "vtkOpenGLTexture",
        ],
        # Properties
        propertySerializer: [
            "vtkProperty",
            "vtkOpenGLProperty",
        ],
        # RenderWindows
        renderWindowSerializer: [
            "vtkRenderWindow",
            "vtkCocoaRenderWindow",
            "vtkXOpenGLRenderWindow",
            "vtkWin32OpenGLRenderWindow",
            "vtkEGLRenderWindow",
            "vtkOpenVRRenderWindow",
            "vtkOpenXRRenderWindow",
            "vtkGenericOpenGLRenderWindow",
            "vtkOSOpenGLRenderWindow",
            "vtkOpenGLRenderWindow",
            "vtkIOSRenderWindow",
            "vtkExternalOpenGLRenderWindow",
            "vtkOffscreenOpenGLRenderWindow",
        ],
        # LookupTables/TransferFunctions
        lookupTableSerializer2: "vtkLookupTable",
        discretizableColorTransferFunctionSerializer: "vtkPVDiscretizableColorTransferFunction",
        colorTransferFunctionSerializer: "vtkColorTransferFunction",
        pwfSerializer: "vtkPiecewiseFunction",
        # VolumeProperty
        volumePropertySerializer: "vtkVolumeProperty",
        # Datasets
        polydataSerializer: "vtkPolyData",
        imagedataSerializer: [
            "vtkImageData",
            "vtkStructuredPoints",
        ],
        mergeToPolydataSerializer: [
            "vtkMultiBlockDataSet",
            "vtkUnstructuredGrid",
        ],
        # Renderers
        rendererSerializer: [
            "vtkRenderer",
            "vtkOpenGLRenderer",
        ],
        # Lights
        lightSerializer: [
            "vtkLight",
            "vtkPVLight",
            "vtkOpenGLLight",
        ],
        # Annotations (ScalarBar/Axes)
        cubeAxesSerializer: "vtkCubeAxesActor",
        scalarBarActorSerializer: "vtkScalarBarActor",
        axesActorSerializer: "vtkAxesActor",
        # Cameras
        cameraSerializer: [
            "vtkCamera",
            "vtkOpenGLCamera",
        ],
    }

    js_classes = {
        "vtkMapper": [
            "vtkCompositePolyDataMapper2",
            "vtkDataSetMapper",
            "vtkOpenGLPolyDataMapper",
            "vtkPolyDataMapper",
        ],
        "vtkVolumeMapper": "vtkFixedPointVolumeRayCastMapper",
        "vtkImageData": "vtkStructuredPoints",
    }

    for serializer, names in serializers.items():
        if not isinstance(names, (list, tuple)):
            names = [names]

        for name in names:
            registerInstanceSerializer(name, serializer)

    for js_class, vtk_classes in js_classes.items():
        if not isinstance(vtk_classes, (list, tuple)):
            vtk_classes = [vtk_classes]

        for vtk_class in vtk_classes:
            registerJSClass(vtk_class, js_class)
