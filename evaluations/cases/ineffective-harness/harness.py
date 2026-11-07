def apply(controller, requested):
    controller["pad_request"] = requested

def game_update(controller):
    return controller.get("latched_pad", 0)
