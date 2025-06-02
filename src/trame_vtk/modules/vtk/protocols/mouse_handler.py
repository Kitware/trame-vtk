import math

from vtkmodules.vtkWebCore import vtkWebInteractionEvent

from wslink import register as export_rpc

from .web_protocol import vtkWebProtocol


def apply_modifiers(event, interactor):
    interactor.SetShiftKey(1 if event.get("shiftKey") else 0)
    interactor.SetControlKey(1 if event.get("ctrlKey") else 0)
    interactor.SetAltKey(1 if event.get("altKey") else 0)
    # interactor.SetMetaKey(1 if event.get("metaKey") else 0)


class vtkWebMouseHandler(vtkWebProtocol):
    """Handle Mouse interaction on any type of view"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_action = "up"

    @export_rpc("viewport.mouse.interaction")
    def mouse_interaction(self, event):
        """
        RPC Callback for mouse interactions.
        """
        view = self.get_view(event["view"])

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
        ret_val = self.app.HandleInteractionEvent(view, pvevent)
        del pvevent

        if event["action"] == "down" and self.last_action != event["action"]:
            # Make sure animation registration is only triggered on the first
            # "down" action.
            self.app.InvokeEvent("StartInteractionEvent")

        if event["action"] == "up" and self.last_action != event["action"]:
            self.app.InvokeEvent("EndInteractionEvent")

        if ret_val:
            self.app.InvokeEvent("UpdateEvent")

        self.last_action = event["action"]

        return ret_val

    @export_rpc("viewport.mouse.zoom.wheel")
    def update_zoomFromWheel(self, event):
        render_window = self.get_view(event["view"])

        if not render_window:
            return

        interactor = render_window.GetInteractor()
        apply_modifiers(event, interactor)

        if "x" in event and "y" in event:
            # Set the mouse position, so that if there are multiple
            # renderers, the interactor can figure out which one should
            # be modified.
            view_size = render_window.GetSize()
            pos_x = math.floor(view_size[0] * event["x"] + 0.5)
            pos_y = math.floor(view_size[1] * event["y"] + 0.5)

            interactor.SetEventPosition(pos_x, pos_y)
            interactor.MouseMoveEvent()

        if "Start" in event["type"]:
            self.app.InvokeEvent("StartInteractionEvent")
            # It seems every time a StartInteractionEvent is sent, a
            # mouse wheel event with the same spin is sent afterward. We
            # don't want to zoom twice, so do not perform a zoom on the
            # StartInteractionEvent.
            return

        if "End" in event["type"]:
            self.app.InvokeEvent("EndInteractionEvent")
            # This is done
            return

        spin_y = event.get("spinY", 0)
        direction = "Backward" if spin_y >= 0 else "Forward"
        method = getattr(interactor, f"MouseWheel{direction}Event")

        style = interactor.GetInteractorStyle()
        prev_motion_factor = style.GetMouseWheelMotionFactor()
        style.SetMouseWheelMotionFactor(prev_motion_factor * abs(spin_y))
        try:
            method()
        finally:
            style.SetMouseWheelMotionFactor(prev_motion_factor)
