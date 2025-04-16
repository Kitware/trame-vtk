#!/usr/bin/env bash

set -e

mkdir -p ./trame_vtk/modules/common/serve
curl https://unpkg.com/vue-vtk-js@3.3.0 -Lo ./trame_vtk/modules/common/serve/trame-vtk.js
curl https://kitware.github.io/vtk-js/examples/OfflineLocalView/OfflineLocalView.html -Lo ./trame_vtk/tools/static_viewer.html

if ! sha256sum --check .externals.sha256 ; then
  echo "Hash(es) for externals differs, please update .externals.sha256"
fi
