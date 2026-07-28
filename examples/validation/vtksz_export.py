import pyvista as pv
from pyvista import examples

pl = pv.Plotter()
# pl.add_mesh(examples.download_st_helens())
# pl.trame.export_vtksz("scene.vtksz")
# pl.trame.export_html("scene.html")

grid = examples.load_explicit_structured()
grid = grid.compute_connections()

pl.add_mesh(grid, show_edges=True)
pl.trame.export_vtksz("grid.vtksz")
pl.trame.export_html("grid.html")
