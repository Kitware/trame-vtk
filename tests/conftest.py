import pytest
from pathlib import Path
from trame_client.utils.testing import FixtureHelper

ROOT_PATH = Path(__file__).parent.parent.absolute()
HELPER = FixtureHelper(ROOT_PATH)


@pytest.fixture()
def baseline_image():
    HELPER.remove_page_urls()
    yield
    HELPER.remove_page_urls()


@pytest.fixture
def server(xprocess, server_path):
    name, Starter, Monitor = HELPER.get_xprocess_args(server_path)

    # ensure process is running and return its logfile
    logfile = xprocess.ensure(name, Starter)
    yield Monitor(logfile[1])

    # clean up whole process tree afterwards
    xprocess.getinfo(name).terminate()
