import asyncio
from pathlib import Path
import pytest
from seleniumbase import SB
from trame_client.utils.testing import set_browser_size, baseline_comparison


BASELINE_TEST = (
    Path(__file__).parent.parent
    / "visual_baseline/test_rendering[examples/validation/VolumeRendering.py]/init/baseline.png"
)


@pytest.mark.parametrize("server_path", ["examples/validation/VolumeRendering.py"])
@pytest.mark.asyncio
async def test_rendering(server, baseline_image):
    with SB() as sb:
        url = f"http://127.0.0.1:{server.port}/"
        sb.open(url)
        set_browser_size(sb, 600, 300)
        sb.assert_exact_text("1", ".readyCount")
        sb.check_window(name="init", level=3)

        # Try to make sure the remote rendering has the proper size
        await asyncio.sleep(0.1)

        # Grab and compare baseline
        baseline_comparison(sb, BASELINE_TEST, 0.1)
