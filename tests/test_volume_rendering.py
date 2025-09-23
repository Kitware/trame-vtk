from pathlib import Path
import time

from playwright.sync_api import expect, sync_playwright
import pytest

from trame_client.utils.testing import (
    assert_screenshot_matches,
    assert_snapshot_matches,
)


@pytest.mark.parametrize("server_path", ["examples/validation/VolumeRendering.py"])
def test_rendering(server, ref_dir: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        url = f"http://127.0.0.1:{server.port}/"
        page.goto(url)

        page.set_viewport_size({"width": 600, "height": 300})

        # Try to make sure the remote rendering has the proper size
        time.sleep(1)

        expect(page.locator(".readyCount")).to_have_text("1")

        assert_snapshot_matches(page, ref_dir, "test_rendering_volume")
        assert_screenshot_matches(page, ref_dir, "test_rendering_volume", threshold=0.1)
