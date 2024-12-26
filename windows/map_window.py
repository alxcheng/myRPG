import pygame
from windows.window import Window
from windows.battle_window import BattleWindow
from battle.actors import Player, Enemy
from battle.groups import Group
class Map:
    """Holds tile data and tile images."""
    def __init__(self, scale=1):
        self.MAP_WIDTH = 20
        self.MAP_HEIGHT = 20
        self.scale = scale

        # 0=free,1=entity,2=wall/boundary,3=interactable, etc.
        self.map_data = [[0]*self.MAP_WIDTH for _ in range(self.MAP_HEIGHT)]

        # Create boundary walls
        self.vertical_line(0)
        self.vertical_line(self.MAP_WIDTH - 1)
        self.horizontal_line(0)
        self.horizontal_line(self.MAP_HEIGHT - 1)

        # Set one tile to '3' => an interactable
        self.set_tile(3, 3, 3)

        # Load tile images
        self.tile_images = []
        tile1 = pygame.image.load('res/img/tiles/tile1.png')
        tile1 = pygame.transform.scale(tile1, 
                    (int(tile1.get_width() * scale), int(tile1.get_height() * scale)))
        self.tile_images.append(tile1)

        tile2 = pygame.image.load('res/img/tiles/tile2.png')
        tile2 = pygame.transform.scale(tile2, 
                    (int(tile2.get_width() * scale), int(tile2.get_height() * scale)))
        self.tile_images.append(tile2)

        tile3 = pygame.image.load('res/img/tiles/tile3.png')
        tile3 = pygame.transform.scale(tile3, 
                    (int(tile3.get_width() * scale), int(tile3.get_height() * scale)))
        self.tile_images.append(tile3)

        self.char_img = tile1  # fallback or dummy

    def vertical_line(self, x):
        for y in range(len(self.map_data)):
            self.map_data[y][x] = 2

    def horizontal_line(self, y):
        for x in range(len(self.map_data[y])):
            self.map_data[y][x] = 2

    def is_free(self, y, x):
        if 0 <= y < self.MAP_HEIGHT and 0 <= x < self.MAP_WIDTH:
            return (self.map_data[y][x] == 0)
        return False

    def get_tile(self, y, x):
        if 0 <= y < self.MAP_HEIGHT and 0 <= x < self.MAP_WIDTH:
            return self.map_data[y][x]
        return None

    def set_tile(self, y, x, val):
        if 0 <= y < self.MAP_HEIGHT and 0 <= x < self.MAP_WIDTH:
            self.map_data[y][x] = val


class BaseEntity:
    """
    A base class for any tile-based, partially moving entity.
    """
    def __init__(self, name, y, x, game_map):
        self.name = name
        self.y = float(y)
        self.x = float(x)
        self.game_map = game_map

        self.speed = 20
        self.facing = 0  # 0=right,1=down,2=left,3=up
        self.moving = False
        self.moving_counter = 0
        self.new_pos = (y, x)
        self.old_pos = (y, x)

    def can_move_to(self, tile_y, tile_x):
        return self.game_map.is_free(tile_y, tile_x)

    def move(self, direction):
        if self.moving:
            return
        self.facing = direction
        old_y, old_x = int(self.y), int(self.x)
        new_y, new_x = old_y, old_x
        if direction == 0: new_x += 1
        elif direction == 1: new_y += 1
        elif direction == 2: new_x -= 1
        elif direction == 3: new_y -= 1

        if not self.can_move_to(new_y, new_x):
            return
        self.moving = True
        self.moving_counter = self.speed
        self.old_pos = (old_y, old_x)
        self.new_pos = (new_y, new_x)
        self.part_move()

    def part_move(self):
        self.moving_counter -= 1
        step = 1 / self.speed
        if self.facing == 0: self.x += step
        elif self.facing == 1: self.y += step
        elif self.facing == 2: self.x -= step
        elif self.facing == 3: self.y -= step

    def update(self):
        if self.moving:
            if self.moving_counter > 0:
                self.part_move()
            else:
                old_y, old_x = self.old_pos
                new_y, new_x = self.new_pos
                self.game_map.set_tile(old_y, old_x, 0)  # clear old
                self.y, self.x = float(new_y), float(new_x)
                self.game_map.set_tile(new_y, new_x, 1)  # occupy new
                self.moving = False

    def interact_tile_in_front(self):
        """
        Check the tile in front. If it's 3 => 'interactable'
        """
        check_y, check_x = int(self.y), int(self.x)
        if self.facing == 0: check_x += 1
        elif self.facing == 1: check_y += 1
        elif self.facing == 2: check_x -= 1
        elif self.facing == 3: check_y -= 1

        return self.game_map.get_tile(check_y, check_x), (check_y, check_x)


class AnimatedPlayerEntity(BaseEntity):
    """
    A PlayerEntity that uses a sprite sheet (actor1.png) for walking/idle animations.
    """
    def __init__(self, name, y, x, game_map):
        super().__init__(name, y, x, game_map)
        original_sheet = pygame.image.load("res/img/player/actor1.png").convert_alpha()

        scale_factor = game_map.scale
        scaled_w = 32 * 3 * scale_factor
        scaled_h = 32 * 3 * scale_factor
        self.sprite_sheet = pygame.transform.scale(original_sheet, (scaled_w, scaled_h))

        self.frame_width = 32 * scale_factor
        self.frame_height = 32 * scale_factor

        down_frames = []
        for col in range(3):
            x_ = col * self.frame_width
            y_ = 0 * self.frame_height
            down_frames.append(self.sprite_sheet.subsurface(pygame.Rect(x_, y_, self.frame_width, self.frame_height)))

        left_frames = []
        for col in range(3):
            x_ = col * self.frame_width
            y_ = 1 * self.frame_height
            left_frames.append(self.sprite_sheet.subsurface(pygame.Rect(x_, y_, self.frame_width, self.frame_height)))

        up_frames = []
        for col in range(3):
            x_ = col * self.frame_width
            y_ = 2 * self.frame_height
            up_frames.append(self.sprite_sheet.subsurface(pygame.Rect(x_, y_, self.frame_width, self.frame_height)))

        right_frames = []
        for surf in left_frames:
            flipped = pygame.transform.flip(surf, True, False)
            right_frames.append(flipped)

        self.anims = [None]*4
        self.anims[0] = right_frames
        self.anims[1] = down_frames
        self.anims[2] = left_frames
        self.anims[3] = up_frames

        self.walk_pattern = [0, 1, 0, 2]
        self.pattern_index = 0
        self.walkCycle = False
        self.frames = 0
        self.base_speed = self.speed

    def process_input(self, keys):
        if self.moving:
            return
        self.speed = self.base_speed
        keys_pressed = False

        if keys[pygame.K_a]:
            self.facing = 2
            keys_pressed = True
        if keys[pygame.K_d]:
            self.facing = 0
            keys_pressed = True
        if keys[pygame.K_w]:
            self.facing = 3
            keys_pressed = True
        if keys[pygame.K_s]:
            self.facing = 1
            keys_pressed = True

        if keys_pressed:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.speed *= 2
            self.move(self.facing)

    def update(self):
        was_moving = self.moving
        super().update()

        keys = pygame.key.get_pressed()
        still_pushing = (keys[pygame.K_a] or keys[pygame.K_d] or 
                         keys[pygame.K_w] or keys[pygame.K_s])

        if self.moving:
            self.walkCycle = True
            if not was_moving:
                self.pattern_index = 1
                self.frames = 0
        else:
            if still_pushing:
                self.walkCycle = True
            else:
                self.walkCycle = False
                self.pattern_index = 0

        self.frames += 1
        if self.walkCycle and (self.frames % 16 == 0):
            self.pattern_index = (self.pattern_index + 1) % len(self.walk_pattern)

    def get_current_frame(self):
        col = self.walk_pattern[self.pattern_index]
        return self.anims[self.facing][col]


class MapWindow(Window):
    def __init__(self, scale=2, screen_width=800, screen_height=600):
        super().__init__()
        self.game_map = Map(scale=scale)
        self.tile_width = self.game_map.tile_images[0].get_width()
        self.tile_height = self.game_map.tile_images[0].get_height()

        # Create a player
        self.player = AnimatedPlayerEntity("Player", 1, 1, self.game_map)
        self.game_map.set_tile(1, 1, 1)

        # Camera
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_speed = 0.1

        self.screen_width = screen_width
        self.screen_height = screen_height

        # We'll store a reference to a BattleWindow, set by main.py
        self.battle_window = None

    def set_battle_window(self, battle_window):
        self.battle_window = battle_window

    def update(self, events):
        if not self.in_focus:
            return

        for event in events:
            if event.type == pygame.KEYUP:
                # On pressing 'E', check if tile in front is interactable:
                if event.key == pygame.K_e:
                    tile_val, coords = self.player.interact_tile_in_front()
                    if tile_val == 3:
                        # Switch to the battle window
                        self.in_focus = False
                        player_group = Group("Players")
                        player_group.add_actor(Player("Player 1"))
                        player_group.add_actor(Player("Player 2"))
                        player_group.add_actor(Player("Player 3"))
                        enemy_group = Group("Enemies")
                        enemy_group.add_actor(Enemy("Enemy 1"))
                        enemy_group.add_actor(Enemy("Enemy 2"))
                        enemy_group.add_actor(Enemy("Enemy 3"))
                        
                        battle_window = BattleWindow(player_group, enemy_group)
                        self.parent.add_window(battle_window)

                        battle_window.in_focus = True

        # Movement
        keys = pygame.key.get_pressed()
        self.player.process_input(keys)
        self.player.update()

        # Camera centering
        target_camera_x = (self.player.x + 0.5) - (self.screen_width / (2 * self.tile_width))
        target_camera_y = (self.player.y + 0.5) - (self.screen_height / (2 * self.tile_height))

        max_cam_x = self.game_map.MAP_WIDTH - (self.screen_width / self.tile_width)
        max_cam_y = self.game_map.MAP_HEIGHT - (self.screen_height / self.tile_height)
        if max_cam_x < 0:
            max_cam_x = 0
        if max_cam_y < 0:
            max_cam_y = 0

        target_camera_x = max(0, min(target_camera_x, max_cam_x))
        target_camera_y = max(0, min(target_camera_y, max_cam_y))

        self.camera_x += (target_camera_x - self.camera_x) * self.camera_speed
        self.camera_y += (target_camera_y - self.camera_y) * self.camera_speed

    def draw(self, surface):
        if not self.in_focus:
            return

        surface.fill((0, 0, 0))

        # Draw map tiles
        for map_y in range(self.game_map.MAP_HEIGHT):
            for map_x in range(self.game_map.MAP_WIDTH):
                tile_val = self.game_map.map_data[map_y][map_x]
                if tile_val == 2:
                    img = self.game_map.tile_images[1]
                elif tile_val == 3:
                    img = self.game_map.tile_images[2]
                else:
                    img = self.game_map.tile_images[0]

                px = (map_x - self.camera_x) * self.tile_width
                py = (map_y - self.camera_y) * self.tile_height
                rect = img.get_rect()
                rect.x = px
                rect.y = py
                surface.blit(img, rect)

        # Draw player
        px = (self.player.x - self.camera_x) * self.tile_width
        py = (self.player.y - self.camera_y) * self.tile_height
        if hasattr(self.player, 'get_current_frame'):
            frame = self.player.get_current_frame()
        else:
            frame = self.game_map.char_img
        player_rect = frame.get_rect()
        player_rect.x = px
        player_rect.y = py
        surface.blit(frame, player_rect)
