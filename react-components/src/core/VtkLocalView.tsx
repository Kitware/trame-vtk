import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
} from "react";

import { LocalView, enableResetCamera } from "./localview";

const DEFAULT_INTERACTOR_SETTINGS = [
  { button: 1, action: "Rotate" },
  { button: 2, action: "Pan" },
  { button: 3, action: "Zoom", scrollEnabled: true },
  { button: 1, action: "Pan", alt: true },
  { button: 1, action: "Zoom", control: true },
  { button: 1, action: "Select", shift: true },
  { button: 1, action: "Roll", alt: true, shift: true },
];

// trame contract: events arrive as on<Name> props;
// names already in handler form ("onReady") are kept as-is
type AnyProps = Record<string, any>;

function makeEmitter(propsRef: { current: AnyProps }) {
  return (name: string, payload?: unknown) => {
    const key = /^on[A-Z]/.test(name)
      ? name
      : `on${name[0].toUpperCase()}${name.slice(1)}`;
    propsRef.current[key]?.(payload);
  };
}

const VtkLocalView = forwardRef<any, AnyProps>(function VtkLocalView(props, ref) {
  const {
    camera = null,
    interactorEvents = ["EndAnimation"],
    interactorSettings = DEFAULT_INTERACTOR_SETTINGS,
    wsClient,
    contextName = "LocalRenderingContext",
    viewState,
    pickingModes = [],
    trame: trameProp,
    slot,
  } = props;
  const trame = trameProp || window.trame;
  const client = wsClient || trame?.client;

  const container = useRef<HTMLDivElement | null>(null);
  const ctx = useRef<any>(null);
  const propsRef = useRef<AnyProps>(props);
  propsRef.current = props;

  // one-time construction
  useEffect(() => {
    const emit = makeEmitter(propsRef);

    // ready flag bridged to the onReady event (vue used a watched ref)
    let readyValue = false;
    const readyRef = {
      get value() {
        return readyValue;
      },
      set value(v) {
        readyValue = v;
        emit("onReady", v);
      },
    };
    const nextTick = (fn: () => void) => Promise.resolve().then(fn);

    let getArray: (hash?: any, binary?: any) => Promise<any> = () =>
      Promise.resolve(null);
    const session = client?.getConnection()?.getSession();
    if (session) {
      getArray = (hash: string, binary: boolean) =>
        session.call("viewport.geometry.array.get", [hash, binary]);
    }
    if (client?.getRemote()?.SyncView?.getArray) {
      getArray = client.getRemote().SyncView.getArray;
    }

    const view = new LocalView(
      contextName,
      propsRef.current.pickingModes || [],
      getArray,
      interactorEvents,
      { emit, nextTick, ready: readyRef },
    );

    const onBoxSelectChange = ({ container: c, selection }: any) => {
      if (propsRef.current.pickingModes?.includes("select")) {
        view.onBoxSelectChange({ selection });
        return;
      }
      if (!propsRef.current.boxSelection || !c) {
        return;
      }
      emit("BoxSelection", {
        selection,
        mode: "local",
        size: view.openglRenderWindow.getSize(),
        camera: view.getCamera(),
      });
    };

    view.updateStyle(
      propsRef.current.interactorSettings || DEFAULT_INTERACTOR_SETTINGS,
      onBoxSelectChange,
    );
    const { onEnter, onLeave, onKeyUp } = enableResetCamera(view);
    const resizeObserver = new ResizeObserver(() => view.resize());

    // Scene updates arrive from several paths (mount-time viewState, the
    // trame.vtk.delta topic, js_call); serialize them so two synchronize()
    // passes never interleave (renderers are swapped during synchronize).
    let updateQueue = Promise.resolve();
    const queueViewState = (state: any) => {
      updateQueue = updateQueue
        .then(() => view.updateViewState(state))
        .catch((e: unknown) => console.error("trame-vtk: view state update failed", e));
      return updateQueue;
    };

    ctx.current = {
      view,
      onBoxSelectChange,
      onEnter,
      onLeave,
      idChanged: false,
      queueViewState,
    };

    const el = container.current as HTMLDivElement;
    view.setContainer(el);
    resizeObserver.observe(el);
    document.addEventListener("keyup", onKeyUp);

    if (propsRef.current.viewState) {
      view.rwId = propsRef.current.viewState.id;
      queueViewState(propsRef.current.viewState);
    }

    const wsSubscription = session?.subscribe(
      "trame.vtk.delta",
      ([deltaState]: any[]) => {
        if (deltaState.id === view.rwId) {
          queueViewState(deltaState);
        }
      },
    );

    return () => {
      view.beforeDelete();
      if (wsSubscription && session) {
        session.unsubscribe(wsSubscription);
      }
      document.removeEventListener("keyup", onKeyUp);
      resizeObserver.disconnect();
      ctx.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client]);

  // prop-driven updates
  useEffect(() => {
    ctx.current?.view.updateStyle(
      interactorSettings,
      ctx.current.onBoxSelectChange,
    );
  }, [interactorSettings]);
  useEffect(() => {
    if (ctx.current) {
      ctx.current.view.pickingModes = pickingModes;
    }
  }, [pickingModes]);
  useEffect(() => {
    const context = ctx.current;
    if (!context || !viewState) return;
    if (viewState.id === context.idChanged) {
      context.idChanged = false;
      context.queueViewState(viewState);
    }
  }, [viewState]);
  useEffect(() => {
    if (camera && ctx.current) {
      ctx.current.view.setCamera(camera);
    }
  }, [camera]);

  // Imperative surface for server js_call and RemoteLocalView composition
  useImperativeHandle(ref, () => ({
    resetCamera: () => ctx.current?.view.resetCamera(),
    getCamera: () => ctx.current?.view.getCamera(),
    setCamera: (v: any) => ctx.current?.view.setCamera(v),
    resize: () => ctx.current?.view.resize(),
    setSynchronizedViewId: (v: any) => {
      const context = ctx.current;
      if (!context) return;
      context.idChanged =
        typeof propsRef.current.viewState?.id === "number" ? Number(v) : v;
      context.view.setSynchronizedViewId(context.idChanged);
    },
    updateViewState: (state: any) => ctx.current?.queueViewState(state),
    captureImage: async (format = "image/png", opts = {}) => {
      const img = await ctx.current?.view.captureImage(format, opts);
      const response = await fetch(img);
      const blob = await response.blob();
      makeEmitter(propsRef)("onImageCapture", blob);
      return blob;
    },
  }));

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        ...(props.style || {}),
      }}
      onMouseEnter={(e: any) => ctx.current?.onEnter(e)}
      onMouseLeave={(e: any) => ctx.current?.onLeave(e)}
      onClick={(e: any) => ctx.current?.view.onClick(e)}
      onMouseMove={(e: any) => ctx.current?.view.onMouseMove(e)}
    >
      <div
        ref={container}
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          overflow: "hidden",
        }}
      />
      {slot ? slot() : null}
    </div>
  );
});

export default VtkLocalView;
