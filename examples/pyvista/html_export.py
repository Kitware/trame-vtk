# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyvista[all]",
# ]
# ///
import pyvista as pv
from pyvista import examples

mesh = examples.load_uniform()
pl = pv.Plotter(shape=(1, 2))
_ = pl.add_mesh(mesh, scalars="Spatial Point Data", show_edges=True)
pl.subplot(0, 1)
_ = pl.add_mesh(mesh, scalars="Spatial Cell Data", show_edges=True)
pl.export_html("pv.html")
