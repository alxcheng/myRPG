# battle/actors.py

from battle.stats import StatLog
from battle.status_effects import *
from battle.turn_log import TurnContext
from battle.arts import *
import copy
class ActorCopy:
    pass

class Actor:
    """Base class for all actors in the game."""
    def __init__(self, name, group=None):
        self.name = name.upper()
        self.group = group
        self.statlog = StatLog(self)
        self.statuslog = StatusLog(self)
        self.artlog = ArtLog(self)
        self.alive = True
        self.position = 0
        self.av = 0  # Position in the group, relevant for AOE targeting
        self.mindset = None  # Permanent status effect
        self.counter = None  # Art to use when attacked

        self.artlog.add_art(Attack())
        self.artlog.add_art(Heal())

        self.encounter = None

    def take_damage(self, amount):
        """Reduce health by the damage amount after applying defense."""
        defense = self.statlog.defense.get()
        damage = max(0, (amount/defense)*amount)
        self.statlog.health.adjust(-damage)
        print(f"{self.name} takes {damage} damage!")
        if self.statlog.health.get() <= 0:
            self.die()
        return damage
    
    def take_true_damage(self, amount):
        """Reduce health by the damage amount without defense."""
        self.statlog.health.adjust(-amount)
        print(f"{self.name} takes {amount} damage!")
        if self.statlog.health.get() <= 0:
            self.die()
    
    def take_true_healing(self, amount):
        self.statlog.health.adjust(amount)
        print(f"{self.name} heals for {amount} health!")

    def die(self):
        """Handle the actor's death."""
        self.alive = False
        print(f"{self.name} has died.")
        if self.group:
            self.group.remove_actor(self)
        if self.encounter:
            self.encounter.remove_actor(self)

    def is_alive(self):
        return self.alive

    def take_turn(self):
        """Defines the actor's turn logic."""
        pass  # To be overridden by subclasses

    def __str__(self):
        return f"{self.name} (HP: {self.statlog.health.get()})"
    
    def __deepcopy__(self, memo):
        fcopy = ActorCopy()
        memo[id(self)] = fcopy
        fcopy.name = copy.deepcopy(self.name, memo)
        fcopy.group = copy.deepcopy(self.group, memo)
        fcopy.statlog = copy.deepcopy(self.statlog, memo)
        fcopy.statuslog = copy.deepcopy(self.statuslog, memo)
        fcopy.artlog = copy.deepcopy(self.artlog, memo)
        fcopy.alive = self.alive
        fcopy.position = self.position
        fcopy.av = self.av
        fcopy.mindset = copy.deepcopy(self.mindset, memo)
        fcopy.counter = copy.deepcopy(self.counter, memo)
        fcopy.encounter = copy.deepcopy(self.encounter, memo)
        return fcopy

class Player(Actor):
    """Player-controlled actor."""
    def __init__(self, name):
        super().__init__(name)
        self.statlog.health.max.set(100)
        self.statlog.health.set(100)
        self.statlog.power.set(10)
        self.statlog.defense.set(10)
        self.statlog.speed.set(10)
        self.statuslog.add_effect(PowerDown("PowerDown", 1, 1))
        self.statuslog.add_effect(SpeedDown("SpeedDown", 1, 1))
        self.artlog.add_art(FastSlash())

    def take_turn(self, target, art):
        """Handle player's turn."""
          # Placeholder for actual art selection
        art.use(target)
        return "Attack", target
 

    def choose_target(self, targets):
        """Let the player choose a target."""
        print("Choose a target:")
        target_dict = {}
        for idx, target in enumerate(targets):
            target_dict[idx] = target
            print(f"{idx}: {target}")
        while True:
            choice = input("Target number: ")
            if choice.isdigit():
                idx = int(choice)
                if 0 <= idx < len(targets):
                    return target_dict[idx]
            print("Invalid choice. Try again.")

   


class Enemy(Actor):
    """AI-controlled enemy actor."""
    def __init__(self, name):
        super().__init__(name)
        self.statlog.health.max.set(100)
        self.statlog.health.set(100)
        self.statlog.power.set(10)
        self.statlog.defense.set(10)
        self.statlog.speed.set(10)
        self.statuslog.add_effect(PowerDown("PowerDown", 1, 1))
        self.statuslog.add_effect(SpeedDown("SpeedDown", 1, 1))

    def take_turn(self, target, art):
        """Handle enemy's turn."""
        print(f"It's {self.name}'s turn.")

     # Placeholder for actual art selection
        art.use(target)
        return "Attack", target

    def enemy_AI(self):
        import random
        art = self.artlog.log["Attack"]
        return random.choice(self.encounter.allies), art
        
class Slime(Enemy):
    def __init__(self, name):
        super().__init__(name)
        self.statlog.health.max.set(100)
        self.statlog.health.set(100)
        self.statlog.power.set(1)
        self.statlog.defense.set(20)
        self.statlog.speed.set(3)

    def enemy_AI(self):
        import random
        highest_poison = 0
        highest_player = None
        for player in self.encounter.allies:
            if player.statuslog.effects:
                for effect in player.statuslog.effects:
                    if effect.name == "Poison":
                        if effect.count > highest_poison:
                            highest_poison = effect.count
                            highest_player = player
        if bool(highest_player):
            return highest_player
        else:
            return random.choice(self.encounter.allies)
