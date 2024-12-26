import pygame
from window_handler import WindowHandler
from windows.map_window import MapWindow
from windows.battle_window import BattleWindow
from battle.actors import Player, Enemy
from battle.groups import Group
from battle.encounter import Encounter

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
BG_COLOR = (0, 0, 0)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Game')

clock = pygame.time.Clock()
FPS = 60
run = True


def main():
    global run

    # 1) Create a WindowHandler
    window_handler = WindowHandler(screen)

    # 2) Create a map window
    map_window = MapWindow(scale=2, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)

    # 3) Create a placeholder battle window (inactive at start)
    #    We'll instantiate it but keep it out of focus initially.
    #    For demonstration, let's set up one player & one enemy.



    # 4) Add both windows to the handler
    window_handler.add_window(map_window)

    # 5) Let the map window know about the battle window

    map_window.in_focus = True

    while run:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                run = False

        # Update & Draw
        window_handler.update(events)
        window_handler.draw()

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
