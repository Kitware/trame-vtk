from typing import Type, Callable, Dict, Optional
from functools import partialmethod

from vtkmodules.vtkInteractionWidgets import (
    vtkAbstractWidget,
    vtkWidgetRepresentation,
)

from vtkmodules.vtkCommonCore import vtkCommand

EventCallback = Callable[[vtkCommand.EventIds, Optional["VtkWidget"]], None]


def callback_wrapper(target: "VtkWidget", callback: EventCallback):
    def wrapped_callback(*args, **kwargs):
        callback(vtkCommand.GetEventIdFromString(args[1]), target, *args[2:], **kwargs)

    return wrapped_callback


class VtkWidget:
    def __init__(self, w: vtkAbstractWidget):
        self._w = w
        self._listeners: Dict[vtkCommand.EventIds, Dict[EventCallback, int]] = {}

    @property
    def vtk_widget(self) -> vtkAbstractWidget:
        return self._w

    @property
    def vtk_representation(self) -> vtkWidgetRepresentation:
        return self._w.GetRepresentation()

    def __getattr__(self, name: str):
        if hasattr(self.vtk_widget, name):
            return getattr(self.vtk_widget, name)
        elif hasattr(self.vtk_representation, name):
            return getattr(self.vtk_representation, name)
        else:
            return super().__getattribute__(name)

    def enable(self):
        self._w.On()

    def disable(self):
        self._w.Off()

    def add_event_listener(
        self, event: vtkCommand.EventIds, listener: EventCallback
    ) -> Callable[[], None]:
        listeners = self._listeners.setdefault(event, {})

        tag = self.vtk_widget.AddObserver(event, callback_wrapper(self, listener))

        listeners[listener] = tag

        def listener_remover():
            self.remove_event_listener(event, listener)

        return listener_remover

    def remove_event_listener(
        self, event: vtkCommand.EventIds, listener: Optional[EventCallback] = None
    ):
        listeners = self._listeners.get(event, {})

        if listener is None:
            for tag in listeners.values():
                self.vtk_widget.RemoveObserver(tag)

            listeners.clear()
        else:
            tag = listeners.pop(listener, None)

            if tag is not None:
                self.vtk_widget.RemoveObserver(tag)


def _to_snake_case(s: str) -> str:
    out = ""

    for c in s:
        if c.isupper():
            out += f"_{c.lower()}"
        else:
            out += c

    return out


# Dynamically add methods to register listeners for each event available on vtkCommand
# For example:
#   - `vtkCommant.InteractionEvent` becomes `VtkWidget.on_interaction()`
#   - `vtkCommant.StartInteractionEvent` becomes `VtkWidget.on_start_interaction()`
#   - etc.
for name in vars(vtkCommand):
    value = getattr(vtkCommand, name)

    if isinstance(value, vtkCommand.EventIds):
        setattr(
            VtkWidget,
            _to_snake_case("on" + name.replace("Event", "")),
            partialmethod(VtkWidget.add_event_listener, value),
        )


WidgetParam = vtkAbstractWidget | Type[vtkAbstractWidget]
RepresentationParam = vtkWidgetRepresentation | Type[vtkWidgetRepresentation]


class WidgetManager:
    def __init__(self, renderer):
        self._renderer = renderer

    @property
    def _window(self):
        return self._renderer.GetRenderWindow()

    @property
    def _interactor(self):
        return self._window.GetInteractor()

    def add_widget(
        self, w: WidgetParam, r: Optional[RepresentationParam] = None
    ) -> VtkWidget:
        raw_widget: vtkAbstractWidget
        raw_representation: Optional[vtkWidgetRepresentation] = None

        if isinstance(r, type) and issubclass(r, vtkWidgetRepresentation):
            raw_representation = r()
        elif isinstance(r, vtkWidgetRepresentation):
            raw_representation = r
        elif r is not None:
            raise TypeError(
                "The r parameter should be one of: vtkWidgetRepresentation | Type[vtkWidgetRepresentation]"
            )

        if isinstance(w, type) and issubclass(w, vtkAbstractWidget):
            raw_widget = w()
            raw_widget.CreateDefaultRepresentation()
        elif isinstance(w, vtkAbstractWidget):
            raw_widget = w
        else:
            raise TypeError(
                "The w parameter should be one of: vtkAbstractWidget | Type[vtkAbstractWidget]"
            )

        if raw_representation is not None:
            raw_widget.SetRepresentation(raw_representation)

        raw_widget.SetInteractor(self._interactor)

        widget = VtkWidget(raw_widget)

        return widget
