import logging

import vtk

from .cache import remove_from_cache
from .registry import SERIALIZERS, class_name
from .widgets import handle_widget

__all__ = ["serialize", "serialize_widget"]

logger = logging.getLogger(__name__)

# Keep track of which warnings have been printed
NO_SERIALIZER_FOR_INSTANCE = {}
DELETE_CALLBACKS = []


def serialize(parent, instance, instance_id, context, depth):
    instance_type = class_name(instance)
    serializer = SERIALIZERS.get(instance_type, None)
    if instance_id not in DELETE_CALLBACKS:
        instance.AddObserver(
            vtk.vtkCommand.DeleteEvent, lambda *_a, **_k: remove(instance_id)
        )
        DELETE_CALLBACKS.append(instance_id)

    if serializer:
        return serializer(parent, instance, instance_id, context, depth)

    if instance_type not in NO_SERIALIZER_FOR_INSTANCE:
        # Only print the warning once for each type of serializer
        logger.warning("!!!No serializer for %s with id %s", instance_type, instance_id)
        NO_SERIALIZER_FOR_INSTANCE[instance_type] = instance_id

    return None


def remove(instance_id):
    remove_from_cache(instance_id)
    DELETE_CALLBACKS.remove(instance_id)


def serialize_widget(dict_out, widget):
    handle_widget(dict_out, widget)
