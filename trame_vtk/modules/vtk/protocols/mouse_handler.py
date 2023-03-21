from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from wslink import register as exportRpc

from .web_protocol import vtkWebProtocol


class vtkWebMouseHandler(vtkWebProtocol):
    """Handle Mouse interaction on any type of view"""

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

        if event["action"] == "down":
            self.getApplication().InvokeEvent("StartInteractionEvent")

        if event["action"] == "up":
            self.getApplication().InvokeEvent("EndInteractionEvent")

        if retVal:
            self.getApplication().InvokeEvent("UpdateEvent")

        return retVal

    @exportRpc("viewport.mouse.zoom.wheel")
    def updateZoomFromWheel(self, event):
        if "Start" in event["type"]:
            self.getApplication().InvokeEvent("StartInteractionEvent")

        renderWindow = self.getView(event["view"])
        if renderWindow and "spinY" in event:
            zoomFactor = 1.0 - event["spinY"] / 10.0

            camera = renderWindow.GetRenderers().GetFirstRenderer().GetActiveCamera()
            fp = camera.GetFocalPoint()
            pos = camera.GetPosition()
            delta = [fp[i] - pos[i] for i in range(3)]
            camera.Zoom(zoomFactor)

            pos2 = camera.GetPosition()
            camera.SetFocalPoint([pos2[i] + delta[i] for i in range(3)])
            renderWindow.Modified()

        if "End" in event["type"]:
            self.getApplication().InvokeEvent("EndInteractionEvent")
