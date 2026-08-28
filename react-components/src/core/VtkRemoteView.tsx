import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
} from "react";

import vtkRemoteView from "@kitware/vtk.js/Rendering/Misc/RemoteView";
import vtkMouseBoxSelectorManipulator from "@kitware/vtk.js/Interaction/Manipulators/MouseBoxSelectorManipulator";
import vtkInteractorStyleManipulator from "@kitware/vtk.js/Interaction/Style/InteractorStyleManipulator";

// trame contract: interactor/picking events arrive as on<Name> props;
// names already in handler form ("onImageCapture") are kept as-is
type AnyProps = Record<string, any>;

function emit(props: AnyProps, name: string, payload?: unknown) {
  const key = /^on[A-Z]/.test(name)
    ? name
    : `on${name[0].toUpperCase()}${name.slice(1)}`;
  props[key]?.(payload);
}

const VtkRemoteView = forwardRef<any, AnyProps>(function VtkRemoteView(props, ref) {
  const {
    viewId = "-1",
    wsClient,
    interactiveRatio,
    interactiveQuality,
    stillRatio,
    stillQuality,
    enablePicking = false,
    interactorEvents = ["EndAnimation"],
    boxSelection = false,
    visible = false,
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
    if (!client) {
      console.error("VtkRemoteView can not be created without a wsClient");
      return undefined;
    }

    const context: any = { connected: false };
    ctx.current = context;

    const viewStream: any = client.getImageStream().createViewStream(viewId);
    viewStream.get("protocol").protocol.setQuality(viewId, 5, 0.1);
    const view: any = vtkRemoteView.newInstance({
      rpcWheelEvent: "viewport.mouse.zoom.wheel",
      viewStream,
    });
    context.view = view;
    context.viewStream = viewStream;

    if (interactiveRatio) view.setInteractiveRatio(Number(interactiveRatio));
    if (interactiveQuality)
      view.setInteractiveQuality(Number(interactiveQuality));
    if (stillRatio) view.setStillRatio(Number(stillRatio));
    if (stillQuality) view.setStillQuality(Number(stillQuality));

    // Interactor events -> on<Name> props
    const interactor = view.getInteractor();
    const subscriptions: any[] = [];
    interactorEvents.forEach((name: string) => {
      subscriptions.push(
        interactor[`on${name}`]((e: unknown) => emit(propsRef.current, name, e)),
      );
    });

    // Box selection
    const interactorManipulator: any = vtkInteractorStyleManipulator.newInstance(
      { enabled: boxSelection } as any,
    );
    const interactorBoxSelection: any =
      vtkMouseBoxSelectorManipulator.newInstance({ button: 1 });
    interactorManipulator.addMouseManipulator(interactorBoxSelection);
    subscriptions.push(
      interactorBoxSelection.onBoxSelectChange(
        ({ container: c, selection }: any) => {
          if (c) {
            const { width, height } = c.getBoundingClientRect();
            const event = { selection, size: [width, height], mode: "remote" };
            emit(propsRef.current, "BoxSelection", event);
            if (propsRef.current.pickingModes?.includes("select")) {
              emit(propsRef.current, "select", { ...event, action: "select" });
            }
          }
        },
      ),
    );
    interactorManipulator.setInteractor(interactor);
    context.interactorManipulator = interactorManipulator;
    context.interactorBoxSelection = interactorBoxSelection;

    let resizeObserver: ResizeObserver | null = null;

    (async () => {
      const el = container.current as HTMLDivElement;
      view.getCanvasView().setUseBackgroundImage(0);
      view.setContainer(el);
      interactorBoxSelection.setContainer(el);
      interactorBoxSelection.setBoxChangeOnClick(enablePicking);

      const session = client.getConnection().getSession();
      view.setSession(session);
      view.setViewId(viewId);

      await Promise.resolve();

      const { width, height } = el.getBoundingClientRect();
      const minSize = width < 10 || height < 10 ? 10 : 0;
      view
        .getCanvasView()
        .setSize(Math.round(width + minSize), Math.round(height + minSize));

      await new Promise<void>((resolve) => {
        const subscription = viewStream.onImageReady(({ image, metadata }: any) => {
          const [w, h] = metadata.size;
          if (w !== image.width || h !== image.height) {
            viewStream.render();
            return;
          }
          const sw = viewStream.getStillRatio() * Math.round(minSize + width);
          const sh = viewStream.getStillRatio() * Math.round(minSize + height);
          if (w === sw && h === sh) {
            subscription.unsubscribe();
            view.getCanvasView().setBackgroundImage(image);
            resolve();
          } else {
            viewStream.render();
          }
        });
        viewStream.endInteraction();
      });

      view.getCanvasView().setUseBackgroundImage(1);
      context.connected = true;

      resizeObserver = new ResizeObserver(view.resize);
      resizeObserver.observe(el);
      context.resizeObserver = resizeObserver;
    })();

    return () => {
      resizeObserver?.disconnect();
      while (subscriptions.length) {
        subscriptions.pop().unsubscribe();
      }
      interactorManipulator.setEnabled(false);
      interactorManipulator.delete();
      interactorBoxSelection.delete();
      view.delete();
      ctx.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [client]);

  // prop-driven updates
  useEffect(() => {
    const context = ctx.current;
    if (context?.connected) {
      context.view.setViewId(viewId);
      context.view.resize();
    }
  }, [viewId]);
  useEffect(() => {
    if (visible && ctx.current) {
      const { view } = ctx.current;
      const canvas = view.getCanvasView();
      const [w, h] = canvas.getSize();
      canvas.setSize(w + 2, h + 2);
      Promise.resolve().then(view.resize);
    }
  }, [visible]);
  useEffect(() => {
    const context = ctx.current;
    if (!context) return;
    context.view.getInteractorStyle().setSendMouseMove(enablePicking);
    context.interactorBoxSelection.setBoxChangeOnClick(enablePicking);
  }, [enablePicking]);
  useEffect(() => {
    if (interactiveRatio && ctx.current)
      ctx.current.view.setInteractiveRatio(interactiveRatio);
  }, [interactiveRatio]);
  useEffect(() => {
    if (interactiveQuality && ctx.current)
      ctx.current.view.setInteractiveQuality(interactiveQuality);
  }, [interactiveQuality]);
  useEffect(() => {
    if (stillRatio && ctx.current) ctx.current.view.setStillRatio(stillRatio);
  }, [stillRatio]);
  useEffect(() => {
    if (stillQuality && ctx.current)
      ctx.current.view.setStillQuality(stillQuality);
  }, [stillQuality]);
  useEffect(() => {
    const context = ctx.current;
    if (!context) return;
    const select = pickingModes.includes("select");
    context.interactorManipulator.setEnabled(select || boxSelection);
    context.view.getInteractorStyle().setEnabled(!select || enablePicking);
  }, [pickingModes, boxSelection, enablePicking]);

  // Picking helpers
  function getScreenEventPositionFor(source: { clientX: number; clientY: number }) {
    const el = container.current;
    if (!el || !ctx.current) return {};
    const bounds = el.getBoundingClientRect();
    const [canvasWidth, canvasHeight] = ctx.current.view
      .getCanvasView()
      .getSize();
    const scaleX = canvasWidth / bounds.width;
    const scaleY = canvasHeight / bounds.height;
    return {
      position: {
        x: scaleX * (source.clientX - bounds.left),
        y: scaleY * (bounds.height - source.clientY + bounds.top),
        z: 0,
      },
      size: [canvasWidth, canvasHeight],
      scale: [scaleX, scaleY],
    };
  }

  const onClick = (e: any) => {
    if (!propsRef.current.pickingModes?.includes("click")) return;
    emit(propsRef.current, "click", {
      mode: "remote",
      action: "click",
      ...getScreenEventPositionFor(e),
    });
  };
  const onMouseMove = (e: any) => {
    if (!propsRef.current.pickingModes?.includes("hover")) return;
    emit(propsRef.current, "hover", {
      mode: "remote",
      action: "hover",
      ...getScreenEventPositionFor(e),
    });
  };

  // Imperative surface for server js_call and RemoteLocalView composition
  useImperativeHandle(ref, () => ({
    render: () => ctx.current?.view.render(),
    resetCamera: () => ctx.current?.view.resetCamera(),
    resize: () => ctx.current?.view.resize(),
    setInteractiveQuality: (v: any) => ctx.current?.view.setInteractiveQuality(v),
    setInteractiveRatio: (v: any) => ctx.current?.view.setInteractiveRatio(v),
    setStillQuality: (v: any) => ctx.current?.view.setStillQuality(v),
    setStillRatio: (v: any) => ctx.current?.view.setStillRatio(v),
    getInteractiveQuality: () => ctx.current?.view.getInteractiveQuality(),
    getInteractiveRatio: () => ctx.current?.view.getInteractiveRatio(),
    getStillQuality: () => ctx.current?.view.getStillQuality(),
    getStillRatio: () => ctx.current?.view.getStillRatio(),
    captureImage: async () => {
      const url = ctx.current?.view.getCanvasView().get("bgImage").bgImage.src;
      const response = await fetch(url);
      const blob = await response.blob();
      emit(propsRef.current, "onImageCapture", blob);
      return blob;
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
      onClick={onClick}
      onMouseMove={onMouseMove}
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

export default VtkRemoteView;
