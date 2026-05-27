from pathlib import Path
import pyvista as pv
from pyvista import examples


def test_export():
    mesh = examples.load_uniform()
    plotter = pv.Plotter(shape=(1, 2))
    plotter.add_mesh(mesh, scalars="Spatial Point Data", show_edges=True)
    plotter.subplot(0, 1)
    plotter.add_mesh(mesh, scalars="Spatial Cell Data", show_edges=True)
    plotter.export_html("pv.html")

    plotter.close()
    assert Path("pv.html").exists()
