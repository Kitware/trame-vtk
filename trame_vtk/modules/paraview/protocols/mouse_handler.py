from wslink import register as export_rpc

from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from .web_protocol import ParaViewWebProtocol


class ParaViewWebMouseHandler(ParaViewWebProtocol):
    def __init__(self, **kwargs):
        super().__init__()
        self.last_action = "up"

    # RpcName: mouse_interaction => viewport.mouse.interaction
    @export_rpc("viewport.mouse.interaction")
    def mouse_interaction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        view = self.get_view(event["view"])

        if hasattr(view, "UseInteractiveRenderingForScreenshots"):
            if event["action"] == "down":
                view.UseInteractiveRenderingForScreenshots = 1
            elif event["action"] == "up":
                view.UseInteractiveRenderingForScreenshots = 0

        buttons = 0
        if event["buttonLeft"]:
            buttons |= vtkWebInteractionEvent.LEFT_BUTTON
        if event["buttonMiddle"]:
            buttons |= vtkWebInteractionEvent.MIDDLE_BUTTON
        if event["buttonRight"]:
            buttons |= vtkWebInteractionEvent.RIGHT_BUTTON

        modifiers = 0
        if event["shiftKey"]:
            modifiers |= vtkWebInteractionEvent.SHIFT_KEY
        if event["ctrlKey"]:
            modifiers |= vtkWebInteractionEvent.CTRL_KEY
        if event["altKey"]:
            modifiers |= vtkWebInteractionEvent.ALT_KEY
        if event["metaKey"]:
            modifiers |= vtkWebInteractionEvent.META_KEY

        pvevent = vtkWebInteractionEvent()
        pvevent.SetButtons(buttons)
        pvevent.SetModifiers(modifiers)
        pvevent.SetX(event["x"])
        pvevent.SetY(event["y"])
        # pvevent.SetKeyCode(event["charCode"])
        ret_val = self.app.HandleInteractionEvent(view.SMProxy, pvevent)
        del pvevent

        if event["action"] == "down" and self.last_action != event["action"]:
            self.app.InvokeEvent("StartInteractionEvent")

        if event["action"] == "up" and self.last_action != event["action"]:
            self.app.InvokeEvent("EndInteractionEvent")

        if ret_val:
            self.app.InvokeEvent("UpdateEvent")

        self.last_action = event["action"]

        return ret_val
