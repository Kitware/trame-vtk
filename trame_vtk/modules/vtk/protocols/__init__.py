from vtkmodules.web.errors import WebDependencyMissingError

try:
    # Ensure these are importable
    from wslink import schedule_callback  # noqa
    from wslink import register as exportRpc  # noqa
    from wslink.websocket import LinkProtocol  # noqa
except ImportError:
    raise WebDependencyMissingError()
