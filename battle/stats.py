class Num:
    def __init__(self, value):
        self.base_value = value
        self.modifiers = []

    def get(self):
        total_mod = sum(self.modifiers)
        return max(0, self.base_value * (1 + total_mod))

    def set(self, value):
        self.base_value = value

    def add_modifier(self, mod):
        self.modifiers.append(mod)

    def clear_modifiers(self):
        self.modifiers = []

class Stat:
    def __init__(self, name, min_value, temp_value, max_value):
        self.name = name
        self.min = Num(min_value)
        self.temp = Num(temp_value)
        self.max = Num(max_value)

    def get(self):
        return self.temp.get()

    def set(self, value):
        val = max(self.min.get(), min(value, self.max.get()))
        self.temp.set(val)

    def adjust(self, amount):
        self.set(self.get() + amount)

class StatLog:
    def __init__(self, actor):
        self.actor = actor
        self.health = Stat("Health", 0, 100, 100)
        self.defense = Stat("Defense", 0, 10, 10)
        self.power = Stat("Power", 0, 10, 10)
        self.speed = Stat("Speed", 1, 10, 10)

        self.stats = {
            "health": self.health,
            "defense": self.defense,
            "power": self.power,
            "speed": self.speed,
        }
