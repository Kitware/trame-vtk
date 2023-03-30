import logging
from .utils import reference_id

logger = logging.getLogger(__name__)


def orientation_marker_widget(map_to_update, widget):
    instance_id = reference_id(widget)
    enabled = widget.GetEnabled()
    interactive = widget.GetInteractive()

    dst_actor = widget.GetOrientationMarker()
    actor_bounds = dst_actor.GetBounds()

    # Search root renderer
    src_renderer = widget.GetDefaultRenderer()
    if src_renderer is None:
        src_renderer = widget.GetCurrentRenderer()
    if src_renderer is None:
        rw = widget.GetInteractor().GetRenderWindow()
        src_renderer = rw.GetRenderers().GetFirstRenderer()

    # Find dst renderer
    dst_renderer = None
    for renderer in src_renderer.GetRenderWindow().GetRenderers():
        if renderer.HasViewProp(dst_actor):
            dst_renderer = renderer
            break

    # Gather info for client
    map_to_update[instance_id] = {
        "srcRenderer": reference_id(src_renderer),
        "dstRenderer": reference_id(dst_renderer),
        "actorBounds": list(actor_bounds),
        "type": "CameraSync",
        "enabled": enabled,
        "interactive": interactive,
    }


UNKNOWN_CLASSES = set()
SERIALIZERS = {
    "vtkOrientationMarkerWidget": orientation_marker_widget,
}


def handle_widget(map_to_update, widget):
    class_name = widget.GetClassName()
    if class_name in SERIALIZERS:
        SERIALIZERS[class_name](map_to_update, widget)
    elif class_name not in UNKNOWN_CLASSES:
        UNKNOWN_CLASSES.add(class_name)
        logger.warning(f"!!!No widget serializer for {class_name}")
