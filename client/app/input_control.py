import sys
import pygame

from pygame.locals import KMOD_CTRL
from pygame.locals import KMOD_SHIFT
from pygame.locals import K_ESCAPE
from pygame.locals import K_F1
from pygame.locals import K_SLASH
from pygame.locals import K_TAB

from pygame.locals import K_h
from pygame.locals import K_i
from pygame.locals import K_q


MAP_DEFAULT_SCALE = 0.1
HERO_DEFAULT_SCALE = 1.0


def exit_game():
    """Shuts down program and PyGame"""
    pygame.quit()
    sys.exit()


class InputControl(object):
    """Class that handles input received such as keyboard and mouse."""

    def __init__(self):
        """Initializes input member variables when instance is created."""
        self.mouse_pos = (0, 0)
        self.mouse_offset = [0.0, 0.0]
        self.wheel_offset = 0.1
        self.wheel_amount = 0.025

        # Modules that input will depend on
        self._hud = None
        self._world = None

    def start(self, hud, world):
        """Assigns other initialized modules that input module needs."""
        self._hud = hud
        self._world = world

    def render(self, display):
        """Does nothing. Input module does not need render anything."""

    def tick(self, clock):
        """Executed each frame. Calls method for parsing input."""
        self.parse_input(clock)

    def _parse_events(self):
        """Parses input events. These events are executed only once when pressing a key."""
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game()
            elif event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    exit_game()
                elif event.key == K_h or (
                    event.key == K_SLASH and pygame.key.get_mods() & KMOD_SHIFT
                ):
                    self._hud.help.toggle()
                elif event.key == K_TAB:
                    # Toggle between hero and map mode
                    if self._world.hero_actor is None:
                        self._world.select_hero_actor()
                        self.wheel_offset = HERO_DEFAULT_SCALE
                        self._hud.notification("Ego Mode")
                    else:
                        self.wheel_offset = MAP_DEFAULT_SCALE
                        self.mouse_offset = [0, 0]
                        self.mouse_pos = [0, 0]
                        self._world.scale_offset = [0, 0]
                        self._world.hero_actor = None
                        self._hud.notification("Map Mode")
                elif event.key == K_F1:
                    self._hud.show_info = not self._hud.show_info
                elif event.key == K_i:
                    self._world.show_actor_ids = not self._world.show_actor_ids

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse wheel for zooming in and out
                if event.button == 4:
                    self.wheel_offset += self.wheel_amount
                    if self.wheel_offset >= 1.0:
                        self.wheel_offset = 1.0
                elif event.button == 5:
                    self.wheel_offset -= self.wheel_amount
                    if self.wheel_offset <= 0.1:
                        self.wheel_offset = 0.1

    def _parse_mouse(self):
        """Parses mouse input"""
        if pygame.mouse.get_pressed()[0]:
            x, y = pygame.mouse.get_pos()
            self.mouse_offset[0] += (1.0 / self.wheel_offset) * (x - self.mouse_pos[0])
            self.mouse_offset[1] += (1.0 / self.wheel_offset) * (y - self.mouse_pos[1])
            self.mouse_pos = (x, y)

    def parse_input(self, clock):
        """Parses the input, which is classified in keyboard events and mouse"""
        self._parse_events()
        self._parse_mouse()

    @staticmethod
    def _is_quit_shortcut(key):
        """Returns True if one of the specified keys are pressed"""
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)
