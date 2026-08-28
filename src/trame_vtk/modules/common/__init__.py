from pathlib import Path

from trame_vtk import __version__

# Compute local path to serve
serve_path = str(Path(__file__).with_name("serve").resolve())
serve_directory = f"__trame_vtk_{__version__}"

# Serve directory for JS/CSS files
serve = {serve_directory: serve_path}


def setup(server, **_kwargs):
    client_type = "vue2"
    if hasattr(server, "client_type"):
        client_type = server.client_type

    if client_type == "react":
        server.enable_module(
            {
                # built by react-components/ (react counterpart of vue-vtk-js)
                "scripts": [f"{serve_directory}/trame-vtk-react.js"],
                "react_use": ["react_vtk"],
            }
        )
    else:
        server.enable_module(
            {
                "scripts": [f"{serve_directory}/trame-vtk.js"],
                "vue_use": ["vue_vtk"],
            }
        )
