import logging

from .registry import class_name, SERIALIZERS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def serialize(parent, instance, instanceId, context, depth):
    instanceType = class_name(instance)
    serializer = SERIALIZERS[instanceType] if instanceType in SERIALIZERS else None

    if serializer:
        return serializer(parent, instance, instanceId, context, depth)

    logger.error(f"!!!No serializer for {instanceType} with id {instanceId}")

    return None
