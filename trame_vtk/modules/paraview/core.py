from paraview import servermanager


def apply_default_interaction_settings():
    # ProxyManager helper
    pxm = servermanager.ProxyManager()

    # Update interaction mode
    interactionProxy = pxm.GetProxy("settings", "RenderViewInteractionSettings")
    interactionProxy.Camera3DManipulators = [
        "Rotate",
        "Pan",
        "Zoom",  # -
        "Pan",
        "Roll",
        "Pan",  # shift
        "Zoom",
        "Rotate",
        "Zoom",  # ctrl
    ]

    # Custom rendering settings
    renderingSettings = pxm.GetProxy("settings", "RenderViewSettings")
    renderingSettings.LODThreshold = 102400
