import logging

from .registry import class_name, SERIALIZERS

logger = logging.getLogger(__name__)


def serialize(parent, instance, instance_id, context, depth):
    instance_type = class_name(instance)
    serializer = SERIALIZERS[instance_type] if instance_type in SERIALIZERS else None

    if serializer:
        return serializer(parent, instance, instance_id, context, depth)

    logger.debug(f"!!!No serializer for {instance_type} with id {instance_id}")

    return None
