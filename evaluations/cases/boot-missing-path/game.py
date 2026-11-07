def boot():
    return "title"

def finish(mode):
    if mode == "campaign":
        return "credits"
    return "title"

def load(record):
    return record["board"]
