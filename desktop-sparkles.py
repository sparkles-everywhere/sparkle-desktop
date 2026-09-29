#!/usr/bin/env python3

import math
import random
import time

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")

from gi.repository import Gtk, Gdk, GLib, GdkX11


# ============================================================
# Configuration
# ============================================================

SPARKLE_COUNT = 20

MIN_SIZE = 3.0
MAX_SIZE = 5.0

MIN_LIFETIME = 1.5
MAX_LIFETIME = 3.0

SPAWN_INTERVAL = 0.05
FRAME_INTERVAL = 16  # ~60 FPS

# Single color: SPARKLE_COLOR = "#EEEEFF"
# Multiple colors: SPARKLE_COLOR = ["#FF0000", "#FF8800", "#FFFF00", "#00FF00", "#0000FF", "#880088", "#FF00FF"]
SPARKLE_COLOR = ["#078D70", "#26CEAA", "#98E8C1", "#FFFFFF", "#7BADE2", "#5049CC", "#3D1A78"]

# Pre-computed constants
RADIANS_PER_DEGREE = math.pi / 180.0

# How far a sparkle can gently drift
WIGGLE_DISTANCE = 4.0

# Rotation amount
MAX_ROTATION = 10.0


# ============================================================
# Sparkle types
# ============================================================

STAR_TYPES = (
    "diamond",
    "hollow_diamond",
    "soft_star",
    "six_point",
    "eight_point",
)


# ============================================================
# Color parsing
# ============================================================


def parse_hex_color(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    elif len(hex_color) == 3:
        r = int(hex_color[0], 16) / 15.0
        g = int(hex_color[1], 16) / 15.0
        b = int(hex_color[2], 16) / 15.0
        return (r, g, b)
    else:
        raise ValueError(f"Invalid hex color: {hex_color}")


def parse_sparkle_colors(color_config):
    """Parse SPARKLE_COLOR config to list of RGB tuples."""
    if isinstance(color_config, str):
        return [parse_hex_color(color_config)]
    elif isinstance(color_config, (list, tuple)):
        return [parse_hex_color(c) for c in color_config]
    elif isinstance(color_config, tuple) and len(color_config) == 3:
        # Already an RGB tuple
        return [color_config]
    else:
        raise ValueError(f"Invalid SPARKLE_COLOR config: {color_config}")


# Parse colors at module level
SPARKLE_COLORS = parse_sparkle_colors(SPARKLE_COLOR)


# ============================================================
# Sparkle object
# ============================================================


class Sparkle:

    def __init__(self, width, height):
        self.reset(width, height)

    def reset(self, width, height):

        self.x = random.uniform(0, width)
        self.y = random.uniform(0, height)

        self.size = random.uniform(
            MIN_SIZE,
            MAX_SIZE
        )

        self.birth = time.monotonic()

        self.lifetime = random.uniform(
            MIN_LIFETIME,
            MAX_LIFETIME
        )

        self.phase = random.uniform(
            0,
            math.tau
        )

        self.wiggle_x = random.uniform(
            0.5,
            1.5
        )

        self.wiggle_y = random.uniform(
            0.5,
            1.5
        )

        self.rotation_phase = random.uniform(
            0,
            math.tau
        )

        self.rotation_speed = random.uniform(
            0.4,
            1.2
        )

        self.star_type = random.choice(
            STAR_TYPES
        )

        self.alpha = random.uniform(
            0.55,
            1.0
        )

        self.color = random.choice(SPARKLE_COLORS)

    def age(self, now):
        return now - self.birth

    def progress(self, now):
        return min(
            self.age(now) / self.lifetime,
            1.0
        )

    def alive(self, now):
        return self.age(now) < self.lifetime

    def position(self, now):

        x = self.x + math.sin(
            now * self.wiggle_x + self.phase
        ) * WIGGLE_DISTANCE

        y = self.y + math.sin(
            now * self.wiggle_y + self.phase * 1.37
        ) * WIGGLE_DISTANCE

        return x, y

    def rotation(self, now):

        return math.sin(
            now * self.rotation_speed
            + self.rotation_phase
        ) * MAX_ROTATION


# ============================================================
# Basic shape helpers
# ============================================================


def diamond(cr, size, hollow=False):

    """
    ✦ / ✧

    Four-point diamond sparkle.
    """

    long = size * 2.0
    short = size * 0.35

    cr.move_to(0, -long)
    cr.line_to(short, -short)
    cr.line_to(long, 0)
    cr.line_to(short, short)
    cr.line_to(0, long)
    cr.line_to(-short, short)
    cr.line_to(-long, 0)
    cr.line_to(-short, -short)
    cr.close_path()

    if hollow:
        cr.stroke()
    else:
        cr.fill()


# Pre-computed angles for 5-point star
_SOFT_STAR_ANGLES = [
    (math.cos(-math.pi / 2 + i * math.pi / 5), math.sin(-math.pi / 2 + i * math.pi / 5))
    for i in range(10)
]

def soft_star(cr, size):

    """
    ⋆

    Five-ish point star with rounded proportions.
    """

    outer = size * 1.8
    inner = size * 0.42

    for i, (cos_a, sin_a) in enumerate(_SOFT_STAR_ANGLES):
        radius = outer if i % 2 == 0 else inner
        x = cos_a * radius
        y = sin_a * radius

        if i == 0:
            cr.move_to(x, y)
        else:
            cr.line_to(x, y)

    cr.close_path()
    cr.fill()


# Pre-computed angles for 6-point star
_SIX_POINT_ANGLES = [
    (math.cos(-math.pi / 2 + i * math.pi / 6), math.sin(-math.pi / 2 + i * math.pi / 6))
    for i in range(12)
]

def six_point(cr, size):

    """
    ✶

    Six-point geometric star.
    """

    outer = size * 1.8
    inner = size * 0.38

    for i, (cos_a, sin_a) in enumerate(_SIX_POINT_ANGLES):
        radius = outer if i % 2 == 0 else inner
        x = cos_a * radius
        y = sin_a * radius

        if i == 0:
            cr.move_to(x, y)
        else:
            cr.line_to(x, y)

    cr.close_path()
    cr.fill()


# Pre-computed angles for 8-point star
_EIGHT_POINT_ANGLES = [
    (math.cos(-math.pi / 2 + i * math.pi / 8), math.sin(-math.pi / 2 + i * math.pi / 8))
    for i in range(16)
]

def eight_point(cr, size):

    """
    ✷

    Eight-point sparkle.
    """

    outer = size * 1.9
    inner = size * 0.32

    for i, (cos_a, sin_a) in enumerate(_EIGHT_POINT_ANGLES):
        radius = outer if i % 2 == 0 else inner
        x = cos_a * radius
        y = sin_a * radius

        if i == 0:
            cr.move_to(x, y)
        else:
            cr.line_to(x, y)

    cr.close_path()
    cr.fill()


# ============================================================
# Draw one sparkle
# ============================================================


def draw_shape(cr, sparkle, size):

    if sparkle.star_type == "diamond":

        diamond(
            cr,
            size,
            hollow=False
        )

    elif sparkle.star_type == "hollow_diamond":

        diamond(
            cr,
            size,
            hollow=True
        )

    elif sparkle.star_type == "soft_star":

        soft_star(
            cr,
            size
        )

    elif sparkle.star_type == "six_point":

        six_point(
            cr,
            size
        )

    elif sparkle.star_type == "eight_point":

        eight_point(
            cr,
            size
        )


def draw_sparkle(cr, sparkle, now):

    progress = sparkle.progress(now)

    # --------------------------------------------------------
    # Fade
    # --------------------------------------------------------

    fade_in = min(
        progress * 5.0,
        1.0
    )

    fade_out = min(
        (1.0 - progress) * 5.0,
        1.0
    )

    alpha = (
        fade_in
        * fade_out
        * sparkle.alpha
    )

    # --------------------------------------------------------
    # Position
    # --------------------------------------------------------

    x, y = sparkle.position(now)

    # --------------------------------------------------------
    # Pulse
    # --------------------------------------------------------

    pulse = (
        1.0
        + math.sin(
            now * 3.0
            + sparkle.phase
        ) * 0.10
    )

    size = sparkle.size * pulse

    # --------------------------------------------------------
    # Rotation
    # --------------------------------------------------------

    rotation = sparkle.rotation(now) * RADIANS_PER_DEGREE

    r, g, b = sparkle.color

    cr.save()

    cr.translate(x, y)
    cr.rotate(rotation)

    # --------------------------------------------------------
    # Soft glow
    #
    # Draw the shape several times at low opacity.
    # This is still much cheaper than text/Pango.
    # --------------------------------------------------------

    cr.set_source_rgba(
        r,
        g,
        b,
        alpha * 0.08
    )

    draw_shape(
        cr,
        sparkle,
        size * 1.8
    )

    cr.set_source_rgba(
        r,
        g,
        b,
        alpha * 0.12
    )

    draw_shape(
        cr,
        sparkle,
        size * 1.35
    )

    # --------------------------------------------------------
    # Main shape
    # --------------------------------------------------------

    cr.set_source_rgba(
        r,
        g,
        b,
        alpha
    )

    if sparkle.star_type == "hollow_diamond":

        cr.set_line_width(
            max(0.7, size * 0.22)
        )

    draw_shape(
        cr,
        sparkle,
        size
    )

    cr.restore()


# ============================================================
# Window
# ============================================================


class SparkleWindow(Gtk.Window):

    def __init__(self):

        super().__init__(
            title="Desktop Sparkles"
        )

        self.set_decorated(False)
        self.set_app_paintable(True)

        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        self.set_keep_above(True)

        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        self.set_accept_focus(False)
        self.set_focus_on_map(False)

        # ----------------------------------------------------
        # Transparent visual
        # ----------------------------------------------------

        screen = self.get_screen()

        visual = screen.get_rgba_visual()

        if visual is not None:
            self.set_visual(visual)

        self.connect(
            "draw",
            self.on_draw
        )

        self.connect(
            "realize",
            self.on_realize
        )

        self.connect(
            "map",
            self.on_map
        )

        # ----------------------------------------------------
        # Full X11 desktop
        # ----------------------------------------------------

        self.screen = screen

        self.width = screen.get_width()
        self.height = screen.get_height()

        self.set_default_size(
            self.width,
            self.height
        )

        self.move(0, 0)

        # ----------------------------------------------------
        # Sparkles
        # ----------------------------------------------------

        self.sparkles = [
            Sparkle(
                self.width,
                self.height
            )
            for _ in range(SPARKLE_COUNT)
        ]

        # ----------------------------------------------------
        # Animation
        # ----------------------------------------------------

        GLib.timeout_add(
            FRAME_INTERVAL,
            self.tick
        )

        GLib.timeout_add(
            50,
            self.spawn_tick
        )

    # ========================================================
    # Click-through
    # ========================================================

    def on_realize(self, widget):

        gdk_window = self.get_window()

        if gdk_window is not None:

            # Put the overlay above normal windows
            gdk_window.raise_()

    def on_map(self, widget):

        gdk_window = self.get_window()

        if gdk_window is not None:

            # Click-through - set after window is mapped
            empty_region = cairo.Region()

            try:
                gdk_window.input_shape_combine_region(
                    empty_region,
                    0,
                    0
                )
            except Exception as e:
                print(f"Warning: Failed to set click-through on first attempt: {e}")
                # Retry after a delay
                GLib.timeout_add(500, self.retry_click_through)

    def retry_click_through(self):
        """Retry setting click-through in case of early startup issues."""
        gdk_window = self.get_window()

        if gdk_window is not None:
            empty_region = cairo.Region()
            try:
                gdk_window.input_shape_combine_region(
                    empty_region,
                    0,
                    0
                )
                print("Click-through successfully applied on retry")
                return False  # Stop retrying
            except Exception as e:
                print(f"Retry failed: {e}, will try again")
                return True  # Continue retrying
        return True  # Continue retrying if window not ready

    # ========================================================
    # Draw
    # ========================================================

    def on_draw(self, widget, cr):

        # Completely transparent background
        cr.set_operator(
            cairo.OPERATOR_CLEAR
        )

        cr.paint()

        cr.set_operator(
            cairo.OPERATOR_OVER
        )

        now = time.monotonic()

        for sparkle in self.sparkles:

            if sparkle.alive(now):

                draw_sparkle(
                    cr,
                    sparkle,
                    now
                )

        return False

    # ========================================================
    # Animation
    # ========================================================

    def tick(self):

        self.queue_draw()

        return True

    # ========================================================
    # Respawn
    # ========================================================

    def spawn_tick(self):

        now = time.monotonic()

        for sparkle in self.sparkles:

            if not sparkle.alive(now):

                sparkle.reset(
                    self.width,
                    self.height
                )

        return True


# ============================================================
# Main
# ============================================================


def main():

    window = SparkleWindow()

    window.show_all()

    # Re-apply click-through after the window is mapped
    GLib.idle_add(window.on_map, window)

    Gtk.main()



if __name__ == "__main__":
    main()
