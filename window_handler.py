class WindowHandler:
    """
    Manages multiple windows. Each window has 'in_focus' to determine
    if it should accept input/draw calls. 
    By default, we pass the Pygame surface (screen) to each window in main.py.
    """
    def __init__(self, screen):
        self.screen = screen
        self.windows = []

    def add_window(self, window):
        self.windows.append(window)
        window.parent = self

    def update(self, events):
        # Windows are updated in order; 
        # only windows with in_focus == True will actually do anything.
        for window in self.windows:
            if window.in_focus:
                window.update(events)

    def draw(self):
        # Draw windows in order
        for window in self.windows:
            if window.in_focus:
                window.draw(self.screen)
