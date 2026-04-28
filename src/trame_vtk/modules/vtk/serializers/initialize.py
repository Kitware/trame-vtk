import logging

from .actors import (
    axes_actor_serializer,
    cube_axes_serializer,
    generic_actor_serializer,
    scalar_bar_actor_serializer,
)
from .data import (
    generic_volume_serializer,
    imagedata_serializer,
    merge_to_polydata_serializer,
    polydata_serializer,
)
from .lights import light_serializer
from .lookup_tables import (
    color_transfer_function_serializer,
    discretizable_color_transfer_function_serializer,
    lookup_table_serializer,
    lookup_table_serializer2,
    pwf_serializer,
)
from .mappers import generic_mapper_serializer, generic_volume_mapper_serializer
from .properties import property_serializer, volume_property_serializer
from .registry import register_instance_serializer, register_js_class
from .render_windows import (
    camera_serializer,
    render_window_serializer,
    renderer_serializer,
)
from .textures import texture_serializer

logger = logging.getLogger(__name__)


class LUTConfig:
    """Configuration globale pour les sérialiseurs VTK"""

    def __init__(self):
        self._convert_lut = False
        self._skip_light = False

    @property
    def convert_lut(self):
        return self._convert_lut

    @convert_lut.setter
    def convert_lut(self, value):
        self._convert_lut = value

    @property
    def skip_light(self):
        return self._skip_light

    @skip_light.setter
    def skip_light(self, value):
        self._skip_light = value

    def encode_lut(self, value=True):
        self._convert_lut = value

    def skip_light(self, value=True):
        self._skip_light = value


vtk_config = LUTConfig()


def encode_lut(value=True):
    vtk_config.convert_lut = value


def skip_light(value=True):
    vtk_config.skip_light = value


def lookup_table_serializer_selector(*args, **kwargs):
    if vtk_config.convert_lut:
        return lookup_table_serializer2(*args, **kwargs)
    return lookup_table_serializer(*args, **kwargs)


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
            "vtkCompositePolyDataMapper",
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
        # lookup_table_serializer: "vtkLookupTable",
        lookup_table_serializer_selector: "vtkLookupTable",
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
        light_serializer: []
        if vtk_config.skip_light
        else [
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
            "vtkCompositePolyDataMapper",
            "vtkCompositePolyDataMapper2",
            "vtkDataSetMapper",
            "vtkOpenGLPolyDataMapper",
            "vtkPolyDataMapper",
        ],
        "vtkVolumeMapper": [
            "vtkFixedPointVolumeRayCastMapper",
            "vtkSmartVolumeMapper",
            "vtkOpenGLGPUVolumeRayCastMapper",
        ],
        "vtkImageData": "vtkStructuredPoints",
    }

    for serializer, names in serializers.items():
        names_list = [names] if not isinstance(names, (list, tuple)) else names

        for name in names_list:
            register_instance_serializer(name, serializer)

    for js_class, vtk_classes in js_classes.items():
        vtk_classes_list = (
            [vtk_classes] if not isinstance(vtk_classes, (list, tuple)) else vtk_classes
        )
        for vtk_class in vtk_classes_list:
            register_js_class(vtk_class, js_class)
