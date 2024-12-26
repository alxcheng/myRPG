# game_logic/turn_log.py

import copy

class TurnLog:
    def __init__(self, encounter):
        self.encounter = encounter
        self.allies = None
        self.enemies = None
        self.all_actors = encounter.enemies + encounter.allies
        self.turn_queue = {}
        self.current_turn = 0
        self.current_mode = "turn_start"

        self.init_turn_order()
        
    
    def init_turn_order(self):
        for actor in self.encounter.all_actors:
            actor.av = 1000.0 / actor.statlog.speed.get()
        self.create_next_turn()
        self.move_turn()

        
    def create_next_turn(self): # Makes TurnContext object and sets actor for next turn
        temp_turn_counter = self.current_turn + 1
        self.turn_queue[temp_turn_counter] = TurnContext(self.encounter)
       
        lowest_actor = min(self.encounter.all_actors, key=lambda actor: actor.av)
        
        self.turn_queue[temp_turn_counter].actor = lowest_actor

        self.update_all_actors_av(lowest_actor.av)

        # Increment the lowest_actor's AV based on their speed
        lowest_actor.av += 1000.0 / lowest_actor.statlog.speed.get()
    
    def simulate_next_turns(self, num_turns):
        simulated_encounter = copy.deepcopy(self.encounter)
        simulated_turn_queue = copy.deepcopy(self.turn_queue)
        temp_turn_counter = self.current_turn +1

        final_text = "\n === TURN ORDER ===\n\n"

        for i in range(num_turns):
            
            simulated_turn_queue[temp_turn_counter] = TurnContext(simulated_encounter)
        
            lowest_actor = min(simulated_encounter.all_actors, key=lambda actor: actor.av)
            
            simulated_turn_queue[temp_turn_counter].actor = lowest_actor

            for actor in simulated_encounter.all_actors:
                actor.av -= lowest_actor.av
            lowest_actor.av += 1000.0 / lowest_actor.statlog.speed.get()

            final_text += "Turn " + str(temp_turn_counter) + ": " + lowest_actor.name + "\n"
        
            temp_turn_counter += 1
        return final_text


        # Increment the lowest_actor's AV based on their speed
        

    def update_all_actors_av(self, current_actor_av):
        """
        Updates all actors' AV by subtracting the current actor's AV.
        This maintains the correct sequence of turns.
        """
        for actor in self.encounter.all_actors:
            actor.av -= current_actor_av

        
    def move_turn(self):
        self.current_turn += 1

    
    def log_turn_start(self):
        self.turn_queue[self.current_turn].set_start_turn_context()

    def log_turn_action(self):
        self.turn_queue[self.current_turn].set_action_turn_context()
 
    def log_turn_end(self):
        self.turn_queue[self.current_turn].set_end_turn_context()

     
        
    def report_turn_log(self):
        for i in self.turn_queue:
            print(f"{i}: {self.turn_queue[i].actor.name}")
            
    
    def update_turn_order(self, actor, turn_context):
        pass
        

class TurnContext:
    def __init__(self, encounter):
        self.encounter = encounter
        self.actor = None
        self.skill_used = None
        self.start_context = None
        self.action_context = None
        self.end_context = None
    def set_start_turn_context(self):
        self.start_context = copy.deepcopy(self.encounter)
        self.start_context.trigger = "turn_start"
    def set_action_turn_context(self):
        self.action_context = copy.deepcopy(self.encounter)
        self.action_context.trigger = "turn_action"
    def set_end_turn_context(self):
        self.end_context = copy.deepcopy(self.encounter)
        self.end_context.trigger = "turn_end"
