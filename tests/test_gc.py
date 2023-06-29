import gc
import inspect

import pytest
import pyvista as pv

from trame.app import get_server
from trame.widgets.vtk import VtkRemoteLocalView

# pytest_plugins = ('pytest_asyncio',)


def _is_vtk(obj):
    try:
        return obj.__class__.__name__.startswith('vtk')
    except Exception:  # old Python sometimes no __class__.__name__
        return False


@pytest.fixture(autouse=True)
def check_gc():
    """Ensure that all VTK objects are garbage-collected by Python.

    This fixture was adapted from PyVista's test suite.
    """
    gc.collect()
    before = {id(o) for o in gc.get_objects() if _is_vtk(o)}

    class GcHandler:
        def __init__(self) -> None:
            # if set to True, will entirely skip checking in this fixture
            self.skip = False

    gc_handler = GcHandler()

    yield gc_handler

    if gc_handler.skip:
        return

    gc.collect()
    after = [o for o in gc.get_objects() if _is_vtk(o) and id(o) not in before]
    msg = 'Not all objects GCed:\n'
    for obj in after:
        cn = obj.__class__.__name__
        cf = inspect.currentframe()
        referrers = [v for v in gc.get_referrers(obj) if v is not after and v is not cf]
        del cf
        for ri, referrer in enumerate(referrers):
            if isinstance(referrer, dict):
                for k, v in referrer.items():
                    if k is obj:
                        referrers[ri] = 'dict: d key'
                        del k, v
                        break
                    elif v is obj:
                        referrers[ri] = f'dict: d[{k!r}]'
                        del k, v
                        break
                    del k, v
                else:
                    referrers[ri] = f'dict: len={len(referrer)}'
            else:
                referrers[ri] = repr(referrer)
            del ri, referrer
        msg += f'{cn}: {referrers}\n'
        del cn, referrers
    assert len(after) == 0, msg


# @pytest.mark.asyncio
# async
def test_gc():
    plotter = pv.Plotter()
    # Add object with data arrays
    plotter.add_mesh(pv.Wavelet())

    server = get_server()

    view = VtkRemoteLocalView(plotter.ren_win, trame_server=server)

    # await server.ready

    # view.release_resources()  # TODO: None type isn't callable?

    plotter.close()  # Assume this works to free its references
