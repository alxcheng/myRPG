# game_logic/status_effects.py

from battle.turn_log import *

class StatusEffect:
    """Represents a status effect applied to an actor."""
    def __init__(self, name, potency, count):
        self.actor = None
        self.name = name
        self.potency = potency
        self.count = count  # Number of turns the effect lasts

    def apply(self, turnlog: TurnLog):
        """
        Apply the status effect to the actor.
        
        :param turnlog: TurnLog object containing relevant information
        """
        raise NotImplementedError("Subclass must implement abstract method")

    def __str__(self):
        return f"{self.name} (Potency: {self.potency}, Count: {self.count})"

class StatusLog:
    """Manages all status effects applied to an actor."""
    def __init__(self, actor):
        self.actor = actor
        self.effects = []

    def add_effect(self, new_effect):
        """Add a new status effect, combining with existing ones if necessary."""
        for effect in self.effects:
            if effect.name == new_effect.name:
                # Combine effects
                effect.potency += new_effect.potency
                effect.count += new_effect.count
                return
        self.effects.append(new_effect)
        new_effect.actor = self.actor

    def process_effects(self, turnlog: TurnLog):
        """Process all status effects based on the given turnlog."""
        # print(f"Entering process_effects for {self.actor.name}")
        # print(f"Number of effects: {len(self.effects)}")
        
        if not self.effects:  # Check if there are any effects to process
            # print(f"No effects to process for {self.actor.name}")
            return turnlog
        
        # print(f"Effects to process: {self.effects}")
        for effect in self.effects[:]:
            # print(f"Processing effect: {effect}")
            effect.apply(turnlog)
            
            if effect.count <= 0:
                self.effects.remove(effect)
                print(f"{effect.name} has expired on {self.actor.name}.")
        
        # print(f"Finished processing effects for {self.actor.name}")
        return turnlog


class Poison(StatusEffect):
    def apply(self, turnlog: TurnLog):
        if turnlog.current_mode == 'turn_start' and turnlog.turn_queue[turnlog.current_turn].actor == self.actor:
            damage = self.potency
            old_health = self.actor.statlog.health.get()
            self.actor.take_true_damage(damage)
            new_health = self.actor.statlog.health.get()
            
            self.count -= 1
            print(f"{self.actor.name} suffers {damage} damage from {self.name}.")

class Bleed(StatusEffect):
    def apply(self, turnlog: TurnLog):
        if turnlog.current_mode == 'turn_start' and turnlog.turn_queue[turnlog.current_turn].actor == self.actor:
            damage = self.potency
            old_health = self.actor.statlog.health.get()
            self.actor.take_true_damage(damage)
            new_health = self.actor.statlog.health.get()
            
            self.count -= 1
            print(f"{self.actor.name} suffers {damage} damage from {self.name}.")

class PowerDown(StatusEffect):
    def apply(self, turnlog: TurnLog):
        if turnlog.current_mode == 'turn_start': 
            percent = self.actor.statlog.health.get()/ self.actor.statlog.health.max.get()
            self.actor.statlog.power.set(self.actor.statlog.power.max.get() * percent)  

            print(f"{self.actor.name} has their power reduced by {100-percent*100}% from {self.name}.")

class SpeedDown(StatusEffect):
    def apply(self, turnlog: TurnLog):
        if turnlog.current_mode == 'turn_start':
            percent = self.actor.statlog.health.get() / self.actor.statlog.health.max.get()
            self.actor.statlog.speed.set(self.actor.statlog.speed.max.get() * percent)  

            print(f"{self.actor.name} has their speed reduced by {100-percent*100}% from {self.name}.")






