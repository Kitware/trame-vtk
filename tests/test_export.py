from pathlib import Path
import pytest
import asyncio
import pyvista as pv
from pyvista import examples


@pytest.mark.asyncio
async def test_export():
    mesh = examples.load_uniform()
    plotter = pv.Plotter(shape=(1, 2))
    plotter.add_mesh(mesh, scalars="Spatial Point Data", show_edges=True)
    plotter.subplot(0, 1)
    plotter.add_mesh(mesh, scalars="Spatial Cell Data", show_edges=True)
    plotter.export_html("pv.html")

    await asyncio.sleep(0.1)
    plotter.close()
    assert Path("pv.html").exists()
