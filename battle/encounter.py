import time
from battle.turn_log import TurnLog
import copy 


class EncounterCopy:
    pass
class Encounter:
    def __init__(self, ally_group, enemy_group):
        self.ally_group = ally_group
        self.enemy_group = enemy_group
        self.all_actors = self.ally_group.actors + self.enemy_group.actors

        for actor in self.all_actors:
            actor.encounter = self

        self.turn_log = TurnLog(self)
        self.current_actor = None

    def remove_actor(self, actor):
        if actor in self.ally_group.actors:
            self.ally_group.remove_actor(actor)
        if actor in self.enemy_group.actors:
            self.enemy_group.remove_actor(actor)
        if actor in self.all_actors:
            self.all_actors.remove(actor)

    def process_turn(self, actor, target, art):
        if actor.is_alive() and target and target.is_alive():
            self.turn_log.log_turn_action()
            actor.take_turn(target, art)
            actor.statuslog.process_effects(self.turn_log)

        # turn_end
        self.turn_log.current_mode = "turn_end"

    def update(self):
        # Check if the battle is over
        if not self.ally_group.is_alive():
            print("Enemies win")
            return
        if not self.enemy_group.is_alive():
            print("Allies win")
            return

        # If we’re in turn_start, apply statuses
        if self.turn_log.current_mode == "turn_start":
            self.turn_log.log_turn_start()
            for actor in self.all_actors:
                if actor.is_alive():
                    actor.statuslog.process_effects(self.turn_log)
            self.turn_log.current_mode = "turn_action"
            return

        # If we’re in turn_action => 
        #   if current_actor is enemy, do enemy AI
        if self.turn_log.current_mode == "turn_action":
            self.current_actor = self.turn_log.turn_queue[self.turn_log.current_turn].actor
            if self.current_actor in self.enemy_group.actors and self.current_actor.is_alive():
                target, art = self.current_actor.enemy_AI()
                if target and art:
                    self.process_turn(self.current_actor, target, art)
            return

        # If we’re in turn_end => finalize turn, create next turn
        if self.turn_log.current_mode == "turn_end":
            self.turn_log.log_turn_end()

            # Remove dead
            for actor in self.all_actors[:]:
                if not actor.is_alive():
                    self.remove_actor(actor)

            # Create next turn
            self.turn_log.create_next_turn()
            self.turn_log.move_turn()
            self.turn_log.current_mode = "turn_start"
    def __deepcopy__(self, memo):
        # Create a new instance of ScreenEncounter
        fcopy = EncounterCopy()
        
        # Copy other relevant attributes


        fcopy.allies = copy.deepcopy(self.allies, memo)
        fcopy.enemies = copy.deepcopy(self.enemies, memo)
        fcopy.all_actors = fcopy.allies + fcopy.enemies
        
        # Update the encounter reference for all actors
        for actor in fcopy.all_actors:
            actor.encounter = fcopy
        
        return fcopy
