import VtkLocalView from "./core/VtkLocalView";
import VtkRemoteLocalView from "./core/VtkRemoteLocalView";
import VtkRemoteView from "./core/VtkRemoteView";

export default {
  VtkLocalView,
  VtkRemoteLocalView,
  VtkRemoteView,
  VtkSyncView: VtkLocalView,
};
