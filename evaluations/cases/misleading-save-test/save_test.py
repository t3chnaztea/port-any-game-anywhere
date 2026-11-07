class Session:
    def __init__(self):
        self.saved = None
    def save(self, state):
        self.saved = state.copy()
    def load(self):
        return self.saved

s = Session()
s.save({"board": 3, "moves": 8, "undo": [1, 2]})
assert s.load()["board"] == 3
print("PASS: save reload")
