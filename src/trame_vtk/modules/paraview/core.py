from paraview import servermanager


def apply_default_interaction_settings():
    # ProxyManager helper
    pxm = servermanager.ProxyManager()

    # Update interaction mode
    interaction_proxy = pxm.GetProxy("settings", "RenderViewInteractionSettings")
    interaction_proxy.Camera3DManipulators = [
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
    rendering_settings = pxm.GetProxy("settings", "RenderViewSettings")
    rendering_settings.LODThreshold = 102400
