class Window:
    """Generic window base class."""
    def __init__(self):
        self.in_focus = False

    def update(self, events):
        pass

    def draw(self, surface):
        pass
