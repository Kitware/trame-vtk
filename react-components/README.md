# trame-vtk react-components

React components for trame VTK views — the react counterpart of
[vue-vtk-js](https://github.com/Kitware/vue-vtk-js) for applications
running the native React client (`client_type="react"`).

Provides `VtkRemoteView`, `VtkLocalView` (alias `VtkSyncView`) and
`VtkRemoteLocalView`, matching the tags emitted by the `trame-vtk` Python
widgets. The scene-synchronization core (`src/core/localview.js`) mirrors
vue-vtk-js's implementation and is kept as plain JS for diffability against
its source of truth.

## Build

```bash
npm install
npm run build   # ../src/trame_vtk/modules/common/serve/trame-vtk-react.js
```

The built bundle embeds vtk.js and expects the page's React
(`window.React`), as provided by the trame react client.

## Develop

```bash
npm run lint
npm run typecheck
```
