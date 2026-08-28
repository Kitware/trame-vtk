// vtk.js does not ship type definitions for all the modules used here
declare module "@kitware/vtk.js/*";

// provided by the trame react client
interface Window {
  trame?: any;
}
