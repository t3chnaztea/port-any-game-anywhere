def boot():
    return "title"

def finish(mode, board):
    if mode == "campaign" and board == 3:
        return "credits"
    if mode == "campaign":
        return board + 1
    raise NotImplementedError("practice completion")

def save(state):
    raise NotImplementedError("disk persistence")
