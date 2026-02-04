from pathlib import Path

from trame_vtk import __version__


# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())
serve_directory = f"__trame_vtk_{__version__}"

# Serve directory for JS/CSS files
serve = {serve_directory: serve_path}

# List of JS files to load (usually from the serve path above)
scripts = [f"{serve_directory}/trame-vtk.js"]

# List of Vue plugins to install/load
vue_use = ["vue_vtk"]
