mkdir -p ./trame_vtk/modules/common/serve
curl https://unpkg.com/vue-vtk-js@3.1.8 -Lo ./trame_vtk/modules/common/serve/trame-vtk.js
curl https://kitware.github.io/vtk-js/examples/OfflineLocalView/OfflineLocalView.html -Lo ./trame_vtk/tools/static_viewer.html