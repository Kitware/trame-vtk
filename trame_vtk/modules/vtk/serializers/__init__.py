import logging
import os

from .mesh import mesh
from .initialize import initialize_serializers
from .serialize import serialize, serialize_widget
from .export import extract_array_hash
from .synchronization_context import SynchronizationContext
from .utils import reference_id
from .initialize import encode_lut, skip_light

logger = logging.getLogger(__name__)
# By default, only show critical messages for serializers
logger.setLevel(logging.CRITICAL)

if "TRAME_SERIALIZE_DEBUG" in os.environ:
    # If this environment variable is set, print out all messages
    logger.setLevel(logging.DEBUG)


def configure_serializer(**options):
    skip_light(options.get("skip_light", True))
    encode_lut(options.get("encode_lut", True))


__all__ = [
    "configure_serializer",
    "encode_lut",
    "skip_light",
    "reference_id",
    "initialize_serializers",
    "mesh",
    "serialize",
    "SynchronizationContext",
    "serialize_widget",
    "extract_array_hash",
]
