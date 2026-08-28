import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";

import VtkRemoteView from "./VtkRemoteView";
import VtkLocalView from "./VtkLocalView";

const BOTTOM_Z_INDEX = { position: "absolute", left: "-20000px" };
const TOP_Z_INDEX = { position: "absolute", left: 0 };

const REMOTE_LOCAL_INTERACTOR_SETTINGS = [
  { button: 1, action: "Rotate" },
  { button: 2, action: "Pan" },
  { button: 3, action: "Zoom", scrollEnabled: true },
  { button: 1, action: "Pan", shift: true },
  { button: 1, action: "Zoom", alt: true },
  { button: 1, action: "Zoom", control: true },
  { button: 1, action: "Roll", alt: true, shift: true },
];

const FORWARDED_INTERACTOR_EVENTS = [
  "StartAnimation",
  "Animation",
  "MouseEnter",
  "MouseLeave",
  "StartMouseMove",
  "MouseMove",
  "EndMouseMove",
  "LeftButtonPress",
  "LeftButtonRelease",
  "MiddleButtonPress",
  "MiddleButtonRelease",
  "RightButtonPress",
  "RightButtonRelease",
  "KeyPress",
  "KeyDown",
  "KeyUp",
  "StartMouseWheel",
  "MouseWheel",
  "EndMouseWheel",
  "StartPinch",
  "Pinch",
  "EndPinch",
  "StartPan",
  "Pan",
  "EndPan",
  "StartRotate",
  "Rotate",
  "EndRotate",
  "Button3D",
  "Move3D",
  "StartPointerLock",
  "EndPointerLock",
  "StartInteraction",
  "Interaction",
  "EndInteraction",
];

type AnyProps = Record<string, any>;

const VtkRemoteLocalView = forwardRef<any, AnyProps>(function VtkRemoteLocalView(props, ref) {
  const {
    mode = "local",
    disableAutoSwitch = false,
    namespace = "",
    viewId = "-1",
    wsClient,
    interactiveRatio,
    interactiveQuality,
    stillRatio,
    stillQuality,
    camera = null,
    interactorEvents = ["EndAnimation"],
    interactorSettings = REMOTE_LOCAL_INTERACTOR_SETTINGS,
    contextName = "LocalRenderingContext",
    enablePicking = false,
    boxSelection = false,
    viewState,
    pickingModes = [],
    trame: trameProp,
    slot,
  } = props;
  const trame = trameProp || window.trame;

  const localRef = useRef<any>(null);
  const remoteRef = useRef<any>(null);
  const propsRef = useRef<AnyProps>(props);
  propsRef.current = props;
  const [localRenderingReady, setLocalRenderingReady] = useState(false);

  const computedLocalReady = disableAutoSwitch || localRenderingReady;
  const useLocal = mode === "local" && computedLocalReady;
  const useRemote = mode === "remote" || !computedLocalReady;
  const cameraKey = namespace ? `${namespace}Camera` : "camera";

  const emit = (name: string, payload?: unknown) => {
    const key = /^on[A-Z]/.test(name)
      ? name
      : `on${name[0].toUpperCase()}${name.slice(1)}`;
    propsRef.current[key]?.(payload);
  };
  const trigger = (name: string, args: unknown[] = [], kwargs: Record<string, unknown> = {}) =>
    trame.trigger(name, args, kwargs);

  useEffect(() => {
    localRef.current?.setSynchronizedViewId(viewId);
  }, [viewId]);

  // Forward every interactor event from the local view + camera sync hooks
  const localEventProps: AnyProps = {};
  FORWARDED_INTERACTOR_EVENTS.forEach((name) => {
    localEventProps[`on${name}`] = (e: unknown) => emit(name, e);
  });
  localEventProps.onEndAnimation = (e: unknown) => {
    trigger(cameraKey, [localRef.current?.getCamera()]);
    emit("EndAnimation", e);
  };
  localEventProps.onResetCamera = () =>
    trigger(cameraKey, [localRef.current?.getCamera()]);
  localEventProps.onBeforeSceneLoaded = () => setLocalRenderingReady(false);
  localEventProps.onReady = (v: boolean) => {
    setLocalRenderingReady(v);
    emit("onReady", v);
  };
  localEventProps.onImageCapture = (e: unknown) => emit("onLocalImageCapture", e);
  localEventProps.onViewStateChange = (e: unknown) => emit("viewStateChange", e);
  localEventProps.onAfterSceneLoaded = (e: unknown) => emit("afterSceneLoaded", e);
  localEventProps.onBoxSelection = (e: unknown) => emit("BoxSelection", e);
  localEventProps.onClick = (e: unknown) => emit("click", e);
  localEventProps.onHover = (e: unknown) => emit("hover", e);
  localEventProps.onSelect = (e: unknown) => emit("select", e);

  // Imperative surface for server js_call
  useImperativeHandle(ref, () => ({
    resetCamera: () =>
      mode === "local" && computedLocalReady
        ? localRef.current?.resetCamera()
        : remoteRef.current?.resetCamera(),
    getCamera: () => localRef.current?.getCamera(),
    setCamera: (v: any) => localRef.current?.setCamera(v),
    setSynchronizedViewId: (v: any) => localRef.current?.setSynchronizedViewId(v),
    updateViewState: (state: any) => localRef.current?.updateViewState(state),
    resize: () => {
      localRef.current?.resize();
      remoteRef.current?.resize();
    },
    captureImage: (format?: string, opts?: unknown) => {
      localRef.current?.captureImage(format, opts);
      remoteRef.current?.captureImage();
    },
  }));

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        zIndex: 0,
        ...(props.style || {}),
      }}
    >
      <VtkLocalView
        ref={localRef}
        pickingModes={pickingModes}
        wsClient={wsClient}
        trame={trame}
        style={useLocal ? TOP_Z_INDEX : BOTTOM_Z_INDEX}
        camera={camera}
        interactorEvents={interactorEvents}
        interactorSettings={interactorSettings}
        contextName={contextName}
        boxSelection={boxSelection}
        viewState={viewState}
        slot={slot}
        {...localEventProps}
      />
      <VtkRemoteView
        ref={remoteRef}
        pickingModes={pickingModes}
        viewId={viewId}
        wsClient={wsClient}
        trame={trame}
        style={useRemote ? TOP_Z_INDEX : BOTTOM_Z_INDEX}
        visible={useRemote}
        interactiveRatio={interactiveRatio}
        interactiveQuality={interactiveQuality}
        stillRatio={stillRatio}
        stillQuality={stillQuality}
        boxSelection={boxSelection}
        enablePicking={enablePicking}
        onImageCapture={(e: unknown) => emit("onRemoteImageCapture", e)}
        onEndAnimation={() => trigger(cameraKey)}
        onBoxSelection={(e: unknown) => emit("BoxSelection", e)}
        onClick={(e: unknown) => emit("click", e)}
        onHover={(e: unknown) => emit("hover", e)}
        onSelect={(e: unknown) => emit("select", e)}
      />
    </div>
  );
});

export default VtkRemoteLocalView;
