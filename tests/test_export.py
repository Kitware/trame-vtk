import asyncio
from pathlib import Path

import pytest
import pyvista as pv
from playwright.async_api import async_playwright
from pyvista import examples

EXPECTED_SCREENSHOT = Path(__file__).with_name("baseline-scene-export.png")
TEST_BASE = (Path(__file__).with_name("refs") / "test_export").resolve()
TEST_BASE.mkdir(exist_ok=True, parents=True)


@pytest.mark.asyncio
async def test_export():
    html_export_file = TEST_BASE / "pv.html"
    data_export_file = TEST_BASE / "scene-export.vtksz"
    screenshot_export_file = TEST_BASE / "scene-export.png"

    mesh = examples.load_uniform()
    plotter = pv.Plotter(shape=(1, 2))
    plotter.add_mesh(mesh, scalars="Spatial Point Data", show_edges=True)
    plotter.subplot(0, 1)
    plotter.add_mesh(mesh, scalars="Spatial Cell Data", show_edges=True)
    plotter.export_html(html_export_file)
    plotter.export_vtksz(data_export_file)

    await asyncio.sleep(0.1)
    plotter.close()

    assert html_export_file.exists()
    assert data_export_file.exists()

    # capture image
    async with async_playwright() as p:
        # Boot up a headless Chromium browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to a website
        await page.set_viewport_size({"width": 600, "height": 300})
        await page.goto(f"file://{html_export_file.resolve().absolute()}")
        await page.screenshot(path=screenshot_export_file)

        # Clean up resource
        await browser.close()

    # Test image
    error = pv.compare_images(screenshot_export_file, EXPECTED_SCREENSHOT)
    assert error < 200
