import logging
import os

from .mesh import mesh
from .initialize import initialize_serializers
from .serialize import serialize, serialize_widget
from .export import extract_array_hash
from .synchronization_context import SynchronizationContext
from .utils import reference_id

logger = logging.getLogger(__name__)
# By default, only show critical messages for serializers
logger.setLevel(logging.CRITICAL)

if "TRAME_SERIALIZE_DEBUG" in os.environ:
    # If this environment variable is set, print out all messages
    logger.setLevel(logging.DEBUG)

__all__ = [
    "reference_id",
    "initialize_serializers",
    "mesh",
    "serialize",
    "SynchronizationContext",
    "serialize_widget",
    "extract_array_hash",
]
