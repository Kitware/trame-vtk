import pytest
from seleniumbase import SB


@pytest.mark.parametrize("server_path", ["examples/validation/PyVistaLookupTable.py"])
def test_reactivity(server, baseline_image):
    with SB() as sb:
        url = f"http://localhost:{server.port}/"
        sb.open(url)
        sb.sleep(1)  # Wait for geometry to arrive
        sb.check_window(name="init", level=3)
