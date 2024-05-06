#!/usr/bin/env bash

set -e

mkdir -p ./trame_vtk/modules/common/serve
curl https://unpkg.com/vue-vtk-js@3.2.1 -Lo ./trame_vtk/modules/common/serve/trame-vtk.js
# echo 19e7c20470b952cc7b38f1434180b5ec ./trame_vtk/modules/common/serve/trame-vtk.js | md5sum -c --status && echo OK
curl https://kitware.github.io/vtk-js/examples/OfflineLocalView/OfflineLocalView.html -Lo ./trame_vtk/tools/static_viewer.html

if ! sha256sum --check .static_viewer.sha256 ; then
  echo "Hash for static_viewer.html differs, please update .static_viewer.sha256"
fi
