from battle.status_effects import *

class Art:
    def __init__(self, name):
        self.name = name
        self.actor = None
        self.side = "Enemy"

    def use(self, target):
        pass

class ArtLog:
    def __init__(self, actor):
        self.actor = actor
        self.log = {}

    def add_art(self, art):
        self.log[art.name] = art
        art.actor = self.actor

class Attack(Art):
    def __init__(self):
        super().__init__("Attack")

    def use(self, target):
        power = self.actor.statlog.power.get()
        damage = target.take_damage(power)
        #target.statuslog.add_effect(Bleed("Bleed", damage, 2))

class Heal(Art):
    def __init__(self):
        super().__init__("Heal")
        self.side = "Ally"

    def use(self, target):
        power = self.actor.statlog.power.get()
        target.take_true_healing(power * 3)

class FastSlash(Art):
    def __init__(self):
        super().__init__("Fast Slash")

    def use(self, target):
        power = self.actor.statlog.power.get()
        target.take_damage(power * 10)
        self.actor.av = 0
