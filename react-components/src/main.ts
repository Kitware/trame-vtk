// Register the OpenGL view-node classes with the vtk.js factory
// (required for local rendering: renderer/actor/mapper nodes)
import "@kitware/vtk.js/Rendering/OpenGL/Profiles/All";

import components from "./components";

// tags used in the serialized trame layout (vue resolves the same names
// from PascalCase; the react client registry uses explicit kebab-case)
const TAGS: Record<string, keyof typeof components> = {
  "vtk-local-view": "VtkLocalView",
  "vtk-remote-local-view": "VtkRemoteLocalView",
  "vtk-remote-view": "VtkRemoteView",
  "vtk-sync-view": "VtkSyncView",
};

interface Registry {
  register(tag: string, component: unknown): void;
}

export function install(registry: Registry) {
  Object.entries(TAGS).forEach(([tag, name]) => {
    registry.register(tag, components[name]);
  });
}

export const {
  VtkLocalView,
  VtkRemoteLocalView,
  VtkRemoteView,
  VtkSyncView,
} = components;
