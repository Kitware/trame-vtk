import logging

from .actors import (
    axes_actor_serializer,
    cube_axes_serializer,
    generic_actor_serializer,
    scalar_bar_actor_serializer,
)
from .data import (
    imagedata_serializer,
    generic_volume_serializer,
    merge_to_polydata_serializer,
    polydata_serializer,
)
from .lights import light_serializer
from .lookup_tables import (
    color_transfer_function_serializer,
    discretizable_color_transfer_function_serializer,
    lookup_table_serializer,
    pwf_serializer,
)
from .mappers import generic_mapper_serializer, generic_volume_mapper_serializer
from .properties import property_serializer, volume_property_serializer
from .registry import register_instance_serializer, register_js_class
from .render_windows import (
    camera_serializer,
    renderer_serializer,
    render_window_serializer,
)
from .textures import texture_serializer

logger = logging.getLogger(__name__)


def initialize_serializers():
    # Define which serializer will be used for which VTK classes
    serializers = {
        # Actors/view_props
        generic_actor_serializer: [
            "vtkActor",
            "vtkOpenGLActor",
            "vtkPVLODActor",
        ],
        # Mappers
        generic_mapper_serializer: [
            "vtkMapper",
            "vtkDataSetMapper",
            "vtkPolyDataMapper",
            "vtkImageDataMapper",
            "vtkOpenGLPolyDataMapper",
            "vtkCompositePolyDataMapper2",
        ],
        # Volume mappers
        generic_volume_mapper_serializer: [
            "vtkVolumeMapper",
            "vtkFixedPointVolumeRayCastMapper",
            "vtkGPUVolumeRayCastMapper",
            "vtkOpenGLGPUVolumeRayCastMapper",
            "vtkSmartVolumeMapper",
        ],
        # Volume/view_props
        generic_volume_serializer: "vtkVolume",
        # Textures
        texture_serializer: [
            "vtkTexture",
            "vtkOpenGLTexture",
        ],
        # Properties
        property_serializer: [
            "vtkProperty",
            "vtkOpenGLProperty",
        ],
        # RenderWindows
        render_window_serializer: [
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
        lookup_table_serializer: "vtkLookupTable",
        discretizable_color_transfer_function_serializer: "vtkPVDiscretizableColorTransferFunction",
        color_transfer_function_serializer: "vtkColorTransferFunction",
        pwf_serializer: "vtkPiecewiseFunction",
        # VolumeProperty
        volume_property_serializer: "vtkVolumeProperty",
        # Datasets
        polydata_serializer: "vtkPolyData",
        imagedata_serializer: [
            "vtkImageData",
            "vtkStructuredPoints",
        ],
        merge_to_polydata_serializer: [
            "vtkMultiBlockDataSet",
            "vtkUnstructuredGrid",
        ],
        # Renderers
        renderer_serializer: [
            "vtkRenderer",
            "vtkOpenGLRenderer",
        ],
        # Lights
        light_serializer: [
            "vtkLight",
            "vtkPVLight",
            "vtkOpenGLLight",
        ],
        # Annotations (ScalarBar/Axes)
        cube_axes_serializer: "vtkCubeAxesActor",
        scalar_bar_actor_serializer: "vtkScalarBarActor",
        axes_actor_serializer: "vtkAxesActor",
        # Cameras
        camera_serializer: [
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
            register_instance_serializer(name, serializer)

    for js_class, vtk_classes in js_classes.items():
        if not isinstance(vtk_classes, (list, tuple)):
            vtk_classes = [vtk_classes]

        for vtk_class in vtk_classes:
            register_js_class(vtk_class, js_class)
