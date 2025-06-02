from trame_client.utils.version import get_version

__version__ = get_version("trame-vtk")


def reference_id(ref):
    if ref:
        try:
            return ref.__this__[1:17]
        except Exception:
            id_str = str(ref)[-12:-1]
            # print('====> fallback ID %s for %s' % (id_str, ref))
            return id_str
    return "0x0"
