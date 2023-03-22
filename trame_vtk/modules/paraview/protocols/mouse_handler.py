from wslink import register as exportRpc

from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from .web_protocol import ParaViewWebProtocol


class ParaViewWebMouseHandler(ParaViewWebProtocol):
    def __init__(self, **kwargs):
        super(ParaViewWebMouseHandler, self).__init__()
        self.lastAction = "up"

    # RpcName: mouseInteraction => viewport.mouse.interaction
    @exportRpc("viewport.mouse.interaction")
    def mouseInteraction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        view = self.getView(event["view"])

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
        retVal = self.getApplication().HandleInteractionEvent(view.SMProxy, pvevent)
        del pvevent

        if event["action"] == "down" and self.lastAction != event["action"]:
            self.getApplication().InvokeEvent("StartInteractionEvent")

        if event["action"] == "up" and self.lastAction != event["action"]:
            self.getApplication().InvokeEvent("EndInteractionEvent")

        if retVal:
            self.getApplication().InvokeEvent("UpdateEvent")

        self.lastAction = event["action"]

        return retVal
