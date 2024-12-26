class Group:
    def __init__(self, name):
        self.name = name
        self.actors = []

    def add_actor(self, actor):
        actor.group = self
        actor.position = len(self.actors)
        self.actors.append(actor)

    def remove_actor(self, actor):
        if actor in self.actors:
            self.actors.remove(actor)
        # Update positions
        for idx, a in enumerate(self.actors):
            a.position = idx

    def is_alive(self):
        return any(actor.is_alive() for actor in self.actors)
