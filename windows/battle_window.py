import pygame
from .window import Window
from battle.turn_log import TurnLog

STATE_PLAYER_INPUT = 0
STATE_ENEMY_TURN   = 1
STATE_ANIMATION    = 2
STATE_BATTLE_END   = 3

SUB_IDLE         = "idle"
SUB_PICK_ART     = "pick_art"
SUB_PICK_TARGET  = "pick_target"

TAB_GROUP   = 0
TAB_ACTION  = 1
TAB_MINDSET = 2
TAB_COUNTER = 3

class BattleEncounter:
    """
    Mixin with the logic from screen_encounter.py (no Raylib UI).
    """
    def __init__(self, ally_group, enemy_group):
        self.ally_group = ally_group
        self.enemy_group = enemy_group
        self.allies = ally_group.actors
        self.enemies = enemy_group.actors
        self.all_actors = self.allies + self.enemies

        self.turnlog = TurnLog(self)
        self.action_time = False
        self.turninfo = ""

        self.current_actor = None
        self.player_choice_art = None
        self.player_choice_target = None
        self.initial = True

        for actor in self.all_actors:
            actor.encounter = self

    def remove_actor(self, actor):
        if actor in self.allies:
            self.allies.remove(actor)
        elif actor in self.enemies:
            self.enemies.remove(actor)
        self.all_actors.remove(actor)

    def remove_dead_actors(self):
        for actor in self.all_actors[:]:
            if not actor.is_alive():
                self.remove_actor(actor)
                self.mode = "turn_end"

    def process_turn(self, actor, target, art):
        self.action_time = False
        if actor.is_alive():
            target = actor.take_turn(target, art)
            actor.statuslog.process_effects(self.turnlog)
        else:
            self.mode = "turn_end"

        self.turnlog.current_mode = "turn_end"
        self.initial = True
        self.player_choice_art = None
        self.player_choice_target = None
        self.action_time = False

    def process_all_effects(self, context):
        for a in self.all_actors:
            if a.is_alive():
                a.statuslog.process_effects(context)

    def encounter_end(self, message):
        print(message)

    def is_battle_over(self):
        return (not self.ally_group.is_alive()) or (not self.enemy_group.is_alive())

    def update_encounter_logic(self):
        self.current_actor = self.turnlog.turn_queue[self.turnlog.current_turn].actor

        # Check if either side is dead
        if not self.ally_group.is_alive():
            self.encounter_end("Enemies win")
            self.parent.windows[0].in_focus = True
            self.parent.windows.pop(1)
            return
        elif not self.enemy_group.is_alive():
            self.encounter_end("Allies win")
            self.parent.windows[0].in_focus = True
            self.parent.windows.pop(1)
            return

        mode = self.turnlog.current_mode

        if mode == "turn_start":
            # Start-of-turn effects
            self.process_all_effects(self.turnlog)
            self.turnlog.current_mode = "turn_action"

        elif mode == "turn_action":
            # We'll let the UI or enemy AI trigger process_turn(...)
            # If the actor died during turn_start (e.g. poison), skip to turn_end
            # instead of waiting forever for input from a dead actor.
            if not self.current_actor.is_alive():
                self.turnlog.current_mode = "turn_end"

        elif mode == "turn_end":
            self.remove_dead_actors()
            self.process_all_effects(self.turnlog)
            self.remove_dead_actors()

            self.turnlog.create_next_turn()
            self.turnlog.move_turn()
            self.turnlog.report_turn_log()

            self.turnlog.current_mode = "turn_start"

class BattleWindow(Window, BattleEncounter):
    def __init__(self, ally_group, enemy_group, on_battle_end=None):
        Window.__init__(self)
        BattleEncounter.__init__(self, ally_group, enemy_group)

        self.state = STATE_PLAYER_INPUT
        self.sub_state = SUB_IDLE

        self.font = pygame.font.SysFont(None, 24)
        self.tabs = ["GROUP", "ACTION", "MINDSET", "COUNTER"]
        self.current_tab_index = 0

        self.selected_art_index = 0
        self.selected_target_index = 0

        # For a small enemy AI "thinking" pause
        self.enemy_delay_start = None
        self.enemy_delay_ms = 600

        self.battle_over = False
        self.on_battle_end = on_battle_end

    def update(self, events):
        if not self.in_focus:
            return

        # 1) Update the logic
        self.update_encounter_logic()

        # 2) If battle is over => call on_battle_end
        if self.is_battle_over() and not self.battle_over:
            self.battle_over = True
            if self.on_battle_end:
                self.on_battle_end()
                self.parent.windows[0].in_focus = True
                self.parent.windows[1].in_focus = False
            return

        # 3) Check the current mode & actor
        mode = self.turnlog.current_mode
        if mode == "turn_action":
            if self.current_actor in self.allies and self.current_actor.is_alive():
                # *** IMPORTANT: Reset sub_state each time we see a new player turn ***
                if self.action_time == False:
                    self.sub_state = SUB_IDLE
                    self.action_time = True

                #print(f"It's {self.current_actor.name}'s turn.")
                self.state = STATE_PLAYER_INPUT
                self.handle_player_input(events)

            elif self.current_actor in self.enemies and self.current_actor.is_alive():
                
                #print(f"It's {self.current_actor.name}'s turn.")
                self.state = STATE_ENEMY_TURN
                self.handle_enemy_turn()

    def draw(self, surface):
        if not self.in_focus:
            return

        surface.fill((30,30,30))

        if self.battle_over:
            msg = "Battle Over!"
            surf = self.font.render(msg, True, (255,0,0))
            surface.blit(surf, (100,100))
            return

        self.draw_tabs(surface)
        self.draw_right_panel(surface)

    # --------------------------
    # Enemy Turn
    # --------------------------
    def handle_enemy_turn(self):
        if self.enemy_delay_start is None:
            self.enemy_delay_start = pygame.time.get_ticks()
            return

        now = pygame.time.get_ticks()
        if (now - self.enemy_delay_start) < self.enemy_delay_ms:
            return

        self.enemy_delay_start = None

        target, art = self.current_actor.enemy_AI()
        self.process_turn(self.current_actor, target, art)

    # --------------------------
    # Player Input
    # --------------------------
    def handle_player_input(self, events):
        if self.sub_state == SUB_IDLE:
            self.handle_tab_navigation(events)
        elif self.sub_state == SUB_PICK_ART:
            self.handle_pick_art_input(events)
        elif self.sub_state == SUB_PICK_TARGET:
            self.handle_pick_target_input(events)
        

    def handle_tab_navigation(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.current_tab_index = (self.current_tab_index - 1) % len(self.tabs)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.current_tab_index = (self.current_tab_index + 1) % len(self.tabs)
                elif event.key in (pygame.K_RETURN, pygame.K_e):
                    if self.current_tab_index == TAB_ACTION:
                        self.sub_state = SUB_PICK_ART
                        self.selected_art_index = 0

    def handle_pick_art_input(self, events):
        arts_list = list(self.current_actor.artlog.log.values())
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.selected_art_index = max(0, self.selected_art_index - 1)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_art_index = min(len(arts_list)-1, self.selected_art_index + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_e):
                    if arts_list:
                        self.player_choice_art = arts_list[self.selected_art_index]
                        self.sub_state = SUB_PICK_TARGET
                        self.selected_target_index = 0
                elif event.key == pygame.K_ESCAPE:
                    self.sub_state = SUB_IDLE

    def handle_pick_target_input(self, events):
        if not self.player_choice_art:
            return

        if self.player_choice_art.side == "Enemy":
            targets = self.enemies
        else:
            targets = self.allies

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.selected_target_index = max(0, self.selected_target_index - 1)
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    self.selected_target_index = min(len(targets)-1, self.selected_target_index + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_e):
                    chosen_target = targets[self.selected_target_index]
                    self.process_turn(self.current_actor, chosen_target, self.player_choice_art)
                elif event.key == pygame.K_ESCAPE:
                    self.sub_state = SUB_PICK_ART

    # --------------------------
    # Drawing
    # --------------------------
    def draw_tabs(self, surface):
        x, y = 20, 50
        for i, name in enumerate(self.tabs):
            color = (255, 255, 0) if i == self.current_tab_index else (255, 255, 255)
            surf = self.font.render(name, True, color)
            surface.blit(surf, (x, y))
            y += 40

    def draw_right_panel(self, surface):
        px, py = 200, 50
        w, h = 400, 300
        pygame.draw.rect(surface, (60,60,60), (px, py, w, h))

        # Show group or action panel
        if self.current_tab_index == TAB_GROUP:
            self.draw_group_info(surface, px, py)
        elif self.current_tab_index == TAB_ACTION:
            self.draw_action_info(surface, px, py)

    def draw_group_info(self, surface, px, py):
        lines = ["=== Allies ==="]
        for ally in self.allies:
            hp_str = f"{ally.statlog.health.get()}/{ally.statlog.health.max.get()}"
            lines.append(f"{ally.name}: HP {hp_str}")
        lines.append("")
        lines.append("=== Enemies ===")
        for enemy in self.enemies:
            hp_str = f"{enemy.statlog.health.get()}/{enemy.statlog.health.max.get()}"
            lines.append(f"{enemy.name}: HP {hp_str}")

        y_off = 10
        for line in lines:
            surf = self.font.render(line, True, (255,255,255))
            surface.blit(surf, (px+10, py+y_off))
            y_off += 25

    def draw_action_info(self, surface, px, py):
        if self.sub_state == SUB_PICK_ART:
            arts_list = list(self.current_actor.artlog.log.values())
            lines = ["=== PICK AN ART ==="]
            for i, art in enumerate(arts_list):
                prefix = ">" if i == self.selected_art_index else " "
                lines.append(f"{prefix} {art.name}")
        elif self.sub_state == SUB_PICK_TARGET and self.player_choice_art:
            if self.player_choice_art.side == "Enemy":
                targets = self.enemies
                side_str = "Enemies"
            else:
                targets = self.allies
                side_str = "Allies"

            lines = [f"=== PICK A TARGET ({side_str}) ==="]
            for i, t in enumerate(targets):
                prefix = ">" if i == self.selected_target_index else " "
                hp_str = f"{t.statlog.health.get()}/{t.statlog.health.max.get()}"
                lines.append(f"{prefix} {t.name} (HP {hp_str})")
        else:
            lines = ["Select an ACTION tab item"]

        y_off = 10
        for line in lines:
            surf = self.font.render(line, True, (255,255,255))
            surface.blit(surf, (px+10, py+y_off))
            y_off += 25
