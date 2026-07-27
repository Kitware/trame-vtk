import pyvista as pv
from pyvista import examples

pl = pv.Plotter()
pl.add_mesh(examples.download_st_helens())
pl.trame.export_vtksz("scene.vtksz")
pl.trame.export_html("scene.html")
