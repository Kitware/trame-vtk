import logging
import os

from .export import extract_array_hash
from .initialize import encode_lut, initialize_serializers, skip_light
from .mesh import mesh
from .serialize import serialize, serialize_widget
from .synchronization_context import SynchronizationContext
from .utils import reference_id

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
    "SynchronizationContext",
    "configure_serializer",
    "encode_lut",
    "extract_array_hash",
    "initialize_serializers",
    "mesh",
    "reference_id",
    "serialize",
    "serialize_widget",
    "skip_light",
]
