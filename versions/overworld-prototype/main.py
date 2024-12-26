import pygame

# ------------------------------------------------------------------------------
# 1. INITIAL SETUP
# ------------------------------------------------------------------------------
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
BG_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

clock = pygame.time.Clock()
FPS = 60
run = True

# ------------------------------------------------------------------------------
# 2. MAP, ENTITIES, AND PLAYER
# ------------------------------------------------------------------------------
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

        self.set_tile(3,3,3)

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
                        (int(tile3.get_width() * scale), int(tile2.get_height() * scale)))
        self.tile_images.append(tile3)


        # Because we now have an animated sprite for the player, 
        # we can choose to not store a single char_img here, 
        # or just leave it if other code references it. 
        # But in the final drawing, we'll rely on the player's animation frames.
        self.char_img = tile1  # dummy or leftover, not used for actual player

    def vertical_line(self, x):
        for y in range(len(self.map_data)):
            self.map_data[y][x] = 2  # boundary

    def horizontal_line(self, y):
        for x in range(len(self.map_data[y])):
            self.map_data[y][x] = 2  # boundary

    def is_free(self, y, x):
        """Return True if the tile is free (==0) and within bounds."""
        if 0 <= y < self.MAP_HEIGHT and 0 <= x < self.MAP_WIDTH:
            return (self.map_data[y][x] == 0)
        return False

    def get_tile(self, y, x):
        """Returns the tile integer (0,1,2,3, etc.) or None if out of bounds."""
        if 0 <= y < self.MAP_HEIGHT and 0 <= x < self.MAP_WIDTH:
            return self.map_data[y][x]
        return None

    def set_tile(self, y, x, val):
        """Sets the tile to val if in bounds."""
        if 0 <= y < self.MAP_HEIGHT and 0 <= x < self.MAP_WIDTH:
            self.map_data[y][x] = val

class BaseEntity:
    """
    A base class for any tile-based, partially moving entity.
      - Checking collisions
      - Partial movement over several frames
      - `update()` to finalize movement
      - `interact()` to check adjacent tile
    """
    def __init__(self, name, y, x, game_map):
        self.name = name
        self.y = float(y)  # allow fractional
        self.x = float(x)
        self.game_map = game_map

        # Movement
        # 0=right,1=down,2=left,3=up
        self.speed = 20
        self.facing = 0
        self.moving = False
        self.moving_counter = 0  # how many frames left in the partial move
        self.new_pos = (y, x)
        self.old_pos = (y, x)

    def can_move_to(self, tile_y, tile_x):
        """Check if the tile is free (==0)."""
        return self.game_map.is_free(tile_y, tile_x)

    def move(self, direction):
        """Initiate a partial movement for 'speed' frames, if not currently moving."""
        if self.moving:
            return  # ignore if mid-move

        self.facing = direction
        old_y, old_x = int(self.y), int(self.x)
        new_y, new_x = old_y, old_x

        if direction == 0:     # right
            new_x += 1
        elif direction == 1:   # down
            new_y += 1
        elif direction == 2:   # left
            new_x -= 1
        elif direction == 3:   # up
            new_y -= 1

        # Check collision
        if not self.can_move_to(new_y, new_x):
            return  # blocked

        # Mark ourselves as moving
        self.moving = True
        self.moving_counter = self.speed
        self.old_pos = (old_y, old_x)
        self.new_pos = (new_y, new_x)

        # immediately do part of the step
        self.part_move()

    def part_move(self):
        """Move 1/self.speed of the distance to the target tile in the facing direction."""
        self.moving_counter -= 1
        step = 1 / self.speed

        if self.facing == 0:   # right
            self.x += step
        elif self.facing == 1: # down
            self.y += step
        elif self.facing == 2: # left
            self.x -= step
        elif self.facing == 3: # up
            self.y -= step

    def update(self):
        """
        If still moving, continue partial movement. 
        Once the move finishes, finalize position in map_data.
        """
        if self.moving:
            if self.moving_counter > 0:
                self.part_move()
            else:
                # finalize
                old_y, old_x = self.old_pos
                new_y, new_x = self.new_pos

                # Clear old tile
                self.game_map.set_tile(old_y, old_x, 0)
                # Snap to new tile
                self.y, self.x = float(new_y), float(new_x)
                # Occupy new tile
                self.game_map.set_tile(new_y, new_x, 1)
                self.moving = False

    def interact(self):
        """
        Check the tile we are facing. If it's 3 => "interactable", otherwise "not".
        """
        check_y, check_x = int(self.y), int(self.x)
        if self.facing == 0:   # right
            check_x += 1
        elif self.facing == 1: # down
            check_y += 1
        elif self.facing == 2: # left
            check_x -= 1
        elif self.facing == 3: # up
            check_y -= 1

        tile_val = self.game_map.get_tile(check_y, check_x)
        if tile_val == 3:
            
            print("interactable")
        else:
            print("not interactable")

# ------------------------------------------------------------------------------
# ANIMATED PLAYER ENTITY
# ------------------------------------------------------------------------------
class AnimatedPlayerEntity(BaseEntity):
    """
    A PlayerEntity that uses a sprite sheet (actor1.png) for walking/idle animations.
    
    Directions: 
      0 -> right
      1 -> down
      2 -> left
      3 -> up
    """
    def __init__(self, name, y, x, game_map):
        super().__init__(name, y, x, game_map)

        # 1) Load the sprite sheet (actor1.png) and scale it up
        original_sheet = pygame.image.load("res/img/player/actor1.png").convert_alpha()

        # The file is 3 rows × 3 columns => 93×93 total, each 31×31
        scale_factor = game_map.scale
        scaled_w = 32 * 3 * scale_factor
        scaled_h = 32 * 3 * scale_factor
        self.sprite_sheet = pygame.transform.scale(original_sheet, (scaled_w, scaled_h))

        self.frame_width = 32 * scale_factor
        self.frame_height = 32 * scale_factor

        # 2) Slice out frames
        #    row0 => down, row1 => left, row2 => up
        #    We'll flip row1 for right => row1 => left, flipped => right
        down_frames = []
        for col in range(3):
            x = col * self.frame_width
            y = 0 * self.frame_height
            down_frames.append(self.sprite_sheet.subsurface(
                pygame.Rect(x, y, self.frame_width, self.frame_height)
            ))

        left_frames = []
        for col in range(3):
            x = col * self.frame_width
            y = 1 * self.frame_height
            left_frames.append(self.sprite_sheet.subsurface(
                pygame.Rect(x, y, self.frame_width, self.frame_height)
            ))

        up_frames = []
        for col in range(3):
            x = col * self.frame_width
            y = 2 * self.frame_height
            up_frames.append(self.sprite_sheet.subsurface(
                pygame.Rect(x, y, self.frame_width, self.frame_height)
            ))

        right_frames = []
        for surf in left_frames:
            flipped = pygame.transform.flip(surf, True, False)
            right_frames.append(flipped)

        # store them by direction index 0=right,1=down,2=left,3=up
        self.anims = [None]*4
        self.anims[0] = right_frames
        self.anims[1] = down_frames
        self.anims[2] = left_frames
        self.anims[3] = up_frames

        # 3) Define the walk pattern. For example: [1,0,2,0] or [0,1,2,1]
        # Let's pick [1,0,2,0] if that's your preference.
        self.walk_pattern = [0, 1, 0, 2]

        self.pattern_index = 0
        self.walkCycle = False
        self.frames = 0

        # Keep base speed from BaseEntity
        self.base_speed = self.speed

    def process_input(self, keys):
        """Same movement logic: W/A/S/D => up/left/down/right, etc."""
        if self.moving:
            return

        # Reset speed
        self.speed = self.base_speed

        keys_pressed = False

        if keys[pygame.K_a]:
            self.facing = 2  # left
            keys_pressed = True
        if keys[pygame.K_d]:
            self.facing = 0  # right
            keys_pressed = True
        if keys[pygame.K_w]:
            self.facing = 3  # up
            keys_pressed = True
        if keys[pygame.K_s]:
            self.facing = 1  # down
            keys_pressed = True

        if keys_pressed:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.speed *= 2
            self.move(self.facing)

    def update(self):
        # 1) Check if we were moving last frame
        was_moving = self.moving

        # 2) Let the parent handle partial movement, collision, etc.
        super().update()

        # 3) Check if we are STILL pressing movement keys
        keys = pygame.key.get_pressed()
        still_pushing = (keys[pygame.K_a] or keys[pygame.K_d] or 
                        keys[pygame.K_w] or keys[pygame.K_s])

        # 4) Are we now mid-move?
        if self.moving:
            self.walkCycle = True

            # If we just STARTED moving this frame (was_moving==False => now True),
            # immediately jump to a walk frame so there's no idle delay
            if not was_moving:
                self.pattern_index = 1  # skip idle frame
                self.frames = 0
        else:
            # If partial move ended, decide if we keep walking or idle
            if still_pushing:
                self.walkCycle = True
            else:
                self.walkCycle = False
                self.pattern_index = 0  # idle

        # 5) If we are walking, step the animation at intervals
        self.frames += 1
        if self.walkCycle and (self.frames % 16 == 0):
            self.pattern_index = (self.pattern_index + 1) % len(self.walk_pattern)


    def get_current_frame(self):
        """
        Return the sub-surface from self.anims based on 
        self.facing and self.walk_pattern[self.pattern_index].
        """
        col = self.walk_pattern[self.pattern_index]
        return self.anims[self.facing][col]

# ------------------------------------------------------------------------------
# 3. WINDOWS & WINDOW HANDLER
# ------------------------------------------------------------------------------
class Window:
    """Generic window base class."""
    def __init__(self):
        self.in_focus = True

    def update(self, events):
        pass

    def draw(self, surface):
        pass

class MapWindow(Window):
    """
    Reverts to using rect.x & rect.y for tile drawing,
    keeps the camera centering & clamping,
    and draws the animated player using get_current_frame().
    """
    def __init__(self, game_map, player):
        super().__init__()
        self.game_map = game_map
        self.player = player

        self.tile_width = self.game_map.tile_images[0].get_width()
        self.tile_height = self.game_map.tile_images[0].get_height()

        self.camera_x = 0.0
        self.camera_y = 0.0
        self.camera_speed = 0.1

    def update(self, events):
        if not self.in_focus:
            return

        # 1) Interactions
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    self.player.interact()

        # 2) Movement
        keys = pygame.key.get_pressed()
        self.player.process_input(keys)
        self.player.update()

        # 3) Camera target so player is centered
        target_camera_x = (self.player.x + 0.5) - (SCREEN_WIDTH / (2 * self.tile_width))
        target_camera_y = (self.player.y + 0.5) - (SCREEN_HEIGHT / (2 * self.tile_height))

        # 4) Clamp
        max_cam_x = self.game_map.MAP_WIDTH - (SCREEN_WIDTH / self.tile_width)
        max_cam_y = self.game_map.MAP_HEIGHT - (SCREEN_HEIGHT / self.tile_height)
        if max_cam_x < 0: 
            max_cam_x = 0
        if max_cam_y < 0: 
            max_cam_y = 0

        target_camera_x = max(0, min(target_camera_x, max_cam_x))
        target_camera_y = max(0, min(target_camera_y, max_cam_y))

        # 5) Smooth camera movement
        self.camera_x += (target_camera_x - self.camera_x) * self.camera_speed
        self.camera_y += (target_camera_y - self.camera_y) * self.camera_speed

    def draw(self, surface):
        if not self.in_focus:
            return

        surface.fill(BG_COLOR)

        # --- Draw all tiles using rect.x, rect.y
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

        # --- Draw the player using their current animation frame
        px = (self.player.x - self.camera_x) * self.tile_width
        py = (self.player.y - self.camera_y) * self.tile_height

        # If the player has get_current_frame (AnimatedPlayerEntity), use it
        if hasattr(self.player, 'get_current_frame'):
            frame = self.player.get_current_frame()
        else:
            # fallback to a single image if not using animation
            frame = self.game_map.char_img

        player_rect = frame.get_rect()
        player_rect.x = px
        player_rect.y = py
        surface.blit(frame, player_rect)

class BattleWindow(Window):
    pass

class WindowHandler:
    """Manages multiple windows."""
    def __init__(self):
        self.windows = []

    def add_window(self, window):
        self.windows.append(window)

    def update(self, events):
        for window in self.windows:
            window.update(events)

    def draw(self):
        for window in self.windows:
            window.draw(screen)

# ------------------------------------------------------------------------------
# 4. MAIN GAME LOOP
# ------------------------------------------------------------------------------
def main():
    global run

    # Create the map
    game_map = Map(scale=2)

    # Create an animated player at (1,1)
    player = AnimatedPlayerEntity("Player", 1, 1, game_map)
    game_map.set_tile(1, 1, 1)

    # Create the MapWindow and WindowHandler
    map_window = MapWindow(game_map, player)
    window_handler = WindowHandler()
    window_handler.add_window(map_window)

    while run:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        window_handler.update(events)
        window_handler.draw()
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    run = True
    main()
