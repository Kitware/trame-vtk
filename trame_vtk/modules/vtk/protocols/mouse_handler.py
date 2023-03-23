import math

from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from wslink import register as exportRpc

from .web_protocol import vtkWebProtocol


class vtkWebMouseHandler(vtkWebProtocol):
    """Handle Mouse interaction on any type of view"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lastAction = "up"

    @exportRpc("viewport.mouse.interaction")
    def mouseInteraction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        view = self.getView(event["view"])

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
        if "x" in event:
            pvevent.SetX(event["x"])
        if "y" in event:
            pvevent.SetY(event["y"])
        if "scroll" in event:
            pvevent.SetScroll(event["scroll"])
        if event["action"] == "dblclick":
            pvevent.SetRepeatCount(2)
        # pvevent.SetKeyCode(event["charCode"])
        retVal = self.getApplication().HandleInteractionEvent(view, pvevent)
        del pvevent

        if event["action"] == "down" and self.lastAction != event["action"]:
            # Make sure animation registration is only triggered on the first
            # "down" action.
            self.getApplication().InvokeEvent("StartInteractionEvent")

        if event["action"] == "up" and self.lastAction != event["action"]:
            self.getApplication().InvokeEvent("EndInteractionEvent")

        if retVal:
            self.getApplication().InvokeEvent("UpdateEvent")

        self.lastAction = event["action"]

        return retVal

    @exportRpc("viewport.mouse.zoom.wheel")
    def updateZoomFromWheel(self, event):
        renderWindow = self.getView(event["view"])

        if not renderWindow:
            return

        interactor = renderWindow.GetInteractor()

        if "x" in event and "y" in event:
            # Set the mouse position, so that if there are multiple
            # renderers, the interactor can figure out which one should
            # be modified.
            viewSize = renderWindow.GetSize()
            posX = math.floor(viewSize[0] * event["x"] + 0.5)
            posY = math.floor(viewSize[1] * event["y"] + 0.5)

            interactor.SetEventPosition(posX, posY)
            interactor.MouseMoveEvent()

        if "Start" in event["type"]:
            self.getApplication().InvokeEvent("StartInteractionEvent")
            # It seems every time a StartInteractionEvent is sent, a
            # mouse wheel event with the same spin is sent afterward. We
            # don't want to zoom twice, so do not perform a zoom on the
            # StartInteractionEvent.
            return

        if "End" in event["type"]:
            self.getApplication().InvokeEvent("EndInteractionEvent")
            # This is done
            return

        spinY = event.get("spinY", 0)
        direction = "Backward" if spinY >= 0 else "Forward"
        method = getattr(interactor, f"MouseWheel{direction}Event")

        style = interactor.GetInteractorStyle()
        prev_motion_factor = style.GetMouseWheelMotionFactor()
        style.SetMouseWheelMotionFactor(abs(spinY))
        try:
            method()
        finally:
            style.SetMouseWheelMotionFactor(prev_motion_factor)
