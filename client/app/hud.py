import os
import math
import carla
import pygame
import datetime

from .color import *

HELP_TEXT = """
Welcome to BounCMPE CarlaSim 2D Visualizer

    TAB          : toggle hero mode
    Mouse Wheel  : zoom in / zoom out
    Mouse Drag   : move map (map mode only)

    F1           : toggle HUD
    I            : toggle actor ids
    H/?          : toggle help
    ESC          : quit
"""


def get_actor_display_name(actor, truncate=250):
    name = " ".join(actor.type_id.replace("_", ".").title().split(".")[1:])
    return (name[: truncate - 1] + "\u2026") if len(name) > truncate else name


class FadingText(object):
    """Renders texts that fades out after some seconds that the user specifies"""

    def __init__(self, font, dim, pos):
        """Initializes variables such as text font, dimensions and position"""
        self.font = font
        self.dim = dim
        self.pos = pos
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)

    def set_text(self, text, color=COLOR_WHITE, seconds=2.0):
        """Sets the text, color and seconds until fade out"""
        text_texture = self.font.render(text, True, color)
        self.surface = pygame.Surface(self.dim)
        self.seconds_left = seconds
        self.surface.fill(COLOR_BLACK)
        self.surface.blit(text_texture, (10, 11))

    def tick(self, clock):
        """Each frame, it shows the displayed text for some specified seconds, if any"""
        delta_seconds = 1e-3 * clock.get_time()
        self.seconds_left = max(0.0, self.seconds_left - delta_seconds)
        self.surface.set_alpha(500.0 * self.seconds_left)

    def render(self, display):
        """Renders the text in its surface and its position"""
        display.blit(self.surface, self.pos)


class HelpText(object):
    def __init__(self, font, width, height):
        """Renders the help text that shows the controls for using no rendering mode"""
        lines = HELP_TEXT.split("\n")
        self.font = font
        self.dim = (680, len(lines) * 22 + 12)
        self.pos = (0.5 * width - 0.5 * self.dim[0], 0.5 * height - 0.5 * self.dim[1])
        self.seconds_left = 0
        self.surface = pygame.Surface(self.dim)
        self.surface.fill(COLOR_BLACK)
        for n, line in enumerate(lines):
            text_texture = self.font.render(line, True, COLOR_WHITE)
            self.surface.blit(text_texture, (22, n * 22))
            self._render = False
        self.surface.set_alpha(220)

    def toggle(self):
        """Toggles display of help text"""
        self._render = not self._render

    def render(self, display):
        """Renders the help text, if enabled"""
        if self._render:
            display.blit(self.surface, self.pos)


class InfoBar(object):
    """Class encharged of rendering the HUD that displays information about the world and the hero vehicle"""

    def __init__(self, width, height):
        """Initializes default HUD params and content data parameters that will be displayed"""
        self.world = None
        self.dim = (width, height)
        self._init_params()
        self._init_data_params()

    def start(self, world):
        self.world = world

    def _init_params(self):
        """Initialized visual parameters such as font text and size"""
        font_name = "courier" if os.name == "nt" else "mono"
        fonts = [x for x in pygame.font.get_fonts() if font_name in x]
        default_font = "ubuntumono"
        mono = default_font if default_font in fonts else fonts[0]
        mono = pygame.font.match_font(mono)
        self._font_mono = pygame.font.Font(mono, 14)
        self._header_font = pygame.font.SysFont("Arial", 14, True)
        self.help = HelpText(pygame.font.Font(mono, 24), *self.dim)
        self._notifications = FadingText(
            pygame.font.Font(pygame.font.get_default_font(), 20),
            (self.dim[0], 40),
            (0, self.dim[1] - 40),
        )

    def _init_data_params(self):
        """Initializes the content data structures"""
        self.show_info = True
        self._info_text = {}

    def notification(self, text, seconds=2.0):
        """Shows fading texts for some specified seconds"""
        self._notifications.set_text(text, seconds=seconds)

    def tick(self, clock):
        hero_mode_text = []
        if self.world.hero_actor is not None:
            hero_speed = self.world.hero_actor.get_velocity()
            hero_speed_text = 3.6 * math.sqrt(
                hero_speed.x**2 + hero_speed.y**2 + hero_speed.z**2
            )

            affected_traffic_light_text = "None"
            if self.world.affected_traffic_light is not None:
                state = self.world.affected_traffic_light.state
                if state == carla.TrafficLightState.Green:
                    affected_traffic_light_text = "GREEN"
                elif state == carla.TrafficLightState.Yellow:
                    affected_traffic_light_text = "YELLOW"
                else:
                    affected_traffic_light_text = "RED"

            affected_speed_limit_text = self.world.hero_actor.get_speed_limit()
            if math.isnan(affected_speed_limit_text):
                affected_speed_limit_text = 0.0
            hero_mode_text = [
                # 'Hero Mode:                 ON',
                "Ego ID:               %7d" % self.world.hero_actor.id,
                "Ego Vehicle:   %14s"
                % get_actor_display_name(self.world.hero_actor, truncate=14),
                "Ego Speed:           %3d km/h" % hero_speed_text,
                # 'Hero Affected by:',
                # '  Traffic Light: %12s' % affected_traffic_light_text,
                # '  Speed Limit:       %3d km/h' % affected_speed_limit_text
            ]
        else:
            hero_mode_text = ["Hero Mode:                OFF"]

        info_text = [
            "Real:    % 16s FPS" % round(1 / self.world.fixed_delta_seconds),
            "Simulated: % 14s FPS" % round(clock.get_fps()),
            "Simulation Time: % 12s"
            % datetime.timedelta(seconds=int(self.world.simulation_time)),
            # 'Map Name:          %10s' % self.town_map.name,
        ]

        self.add_info("SIMULATION", info_text)
        self.add_info("EGO VEHICLE", hero_mode_text)

        self._notifications.tick(clock)

    # def _show_nearby_vehicles(self, vehicles):
    #     """Shows nearby vehicles of the hero actor"""
    #     info_text = []
    #     if self.world.hero_actor is not None and len(vehicles) > 1:
    #         location = self.world.hero_transform.location
    #         vehicle_list = [x[0] for x in vehicles if x[0].id != self.world.hero_actor.id]

    #         def distance(v): return location.distance(v.get_location())
    #         for n, vehicle in enumerate(sorted(vehicle_list, key=distance)):
    #             if n > 15:
    #                 break
    #             vehicle_type = get_actor_display_name(vehicle, truncate=22)
    #             info_text.append('% 5d %s' % (vehicle.id, vehicle_type))
    #     self.add_info('NEARBY VEHICLES', info_text)

    def add_info(self, title, info):
        """Adds a block of information in the left HUD panel of the visualizer"""
        self._info_text[title] = info

    def render(self, display):
        """If flag enabled, it renders all the information regarding the left panel of the visualizer"""
        if self.show_info:
            info_surface = pygame.Surface((240, self.dim[1]))
            info_surface.set_alpha(100)
            display.blit(info_surface, (0, 0))
            v_offset = 4
            bar_h_offset = 100
            bar_width = 106
            i = 0
            for title, info in self._info_text.items():
                if not info:
                    continue
                surface = self._header_font.render(
                    title, True, COLOR_ALUMINIUM_0
                ).convert_alpha()
                display.blit(surface, (8 + bar_width / 2, 18 * i + v_offset))
                v_offset += 12
                i += 1
                for item in info:
                    if v_offset + 18 > self.dim[1]:
                        break
                    if isinstance(item, list):
                        if len(item) > 1:
                            points = [
                                (x + 8, v_offset + 8 + (1.0 - y) * 30)
                                for x, y in enumerate(item)
                            ]
                            pygame.draw.lines(display, (255, 136, 0), False, points, 2)
                        item = None
                    elif isinstance(item, tuple):
                        if isinstance(item[1], bool):
                            rect = pygame.Rect((bar_h_offset, v_offset + 8), (6, 6))
                            pygame.draw.rect(
                                display, COLOR_ALUMINIUM_0, rect, 0 if item[1] else 1
                            )
                        else:
                            rect_border = pygame.Rect(
                                (bar_h_offset, v_offset + 8), (bar_width, 6)
                            )
                            pygame.draw.rect(display, COLOR_ALUMINIUM_0, rect_border, 1)
                            f = (item[1] - item[2]) / (item[3] - item[2])
                            if item[2] < 0.0:
                                rect = pygame.Rect(
                                    (bar_h_offset + f * (bar_width - 6), v_offset + 8),
                                    (6, 6),
                                )
                            else:
                                rect = pygame.Rect(
                                    (bar_h_offset, v_offset + 8), (f * bar_width, 6)
                                )
                            pygame.draw.rect(display, COLOR_ALUMINIUM_0, rect)
                        item = item[0]
                    if item:  # At this point has to be a str.
                        surface = self._font_mono.render(
                            item, True, COLOR_ALUMINIUM_0
                        ).convert_alpha()
                        display.blit(surface, (8, 18 * i + v_offset))
                    v_offset += 18
                v_offset += 24

        self._notifications.render(display)
        self.help.render(display)
