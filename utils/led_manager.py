"""
NeoPixel LED management for MacroPad games.

Provides color constants, animations, and utility functions.
"""

import time
import random


class LEDManager:
    """Manages NeoPixel LEDs on the MacroPad."""

    # Color constants (RGB tuples, 0-255)
    COLORS = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 128, 0),
        'purple': (128, 0, 255),
        'pink': (255, 105, 180),
        'white': (255, 255, 255),
        'off': (0, 0, 0),
    }

    # Game-specific color set for random selection
    GAME_COLORS = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']

    def __init__(self, macropad):
        """
        Initialize the LED manager.

        Args:
            macropad: Adafruit MacroPad object
        """
        self.macropad = macropad
        self.pixels = macropad.pixels
        self.brightness = 0.5
        self.pixels.brightness = self.brightness

    def set_key(self, key_index, color):
        """
        Set a single key's LED color.

        Args:
            key_index: Integer 0-11
            color: RGB tuple or color name string
        """
        if isinstance(color, str):
            color = self.COLORS.get(color, self.COLORS['off'])
        self.pixels[key_index] = color

    def set_all(self, color):
        """
        Set all keys to the same color.

        Args:
            color: RGB tuple or color name string
        """
        if isinstance(color, str):
            color = self.COLORS.get(color, self.COLORS['off'])
        self.pixels.fill(color)

    def clear_all(self):
        """Turn off all LEDs."""
        self.pixels.fill(self.COLORS['off'])

    def get_random_color(self):
        """
        Return a random color from GAME_COLORS.

        Returns:
            Tuple of (color_rgb, color_name)
        """
        color_name = random.choice(self.GAME_COLORS)
        return self.COLORS[color_name], color_name

    def get_color(self, color_name):
        """
        Get RGB tuple for a color name.

        Args:
            color_name: String color name

        Returns:
            RGB tuple
        """
        return self.COLORS.get(color_name, self.COLORS['off'])

    def flash_key(self, key_index, color, times=3, on_time=0.1, off_time=0.1):
        """
        Flash a single key.

        Args:
            key_index: Integer 0-11
            color: RGB tuple or color name string
            times: Number of flashes
            on_time: Duration LED is on per flash
            off_time: Duration LED is off between flashes
        """
        for _ in range(times):
            self.set_key(key_index, color)
            time.sleep(on_time)
            self.set_key(key_index, 'off')
            time.sleep(off_time)

    def flash_all(self, color, times=3, on_time=0.1, off_time=0.1):
        """
        Flash all keys simultaneously.

        Args:
            color: RGB tuple or color name string
            times: Number of flashes
            on_time: Duration LEDs are on per flash
            off_time: Duration LEDs are off between flashes
        """
        for _ in range(times):
            self.set_all(color)
            time.sleep(on_time)
            self.clear_all()
            time.sleep(off_time)

    def sweep_animation(self, color, delay=0.05):
        """
        Sweep color across all keys left-to-right, top-to-bottom.

        Args:
            color: RGB tuple or color name string
            delay: Delay between each key
        """
        # Sweep on
        for i in range(12):
            self.set_key(i, color)
            time.sleep(delay)
        # Sweep off
        for i in range(12):
            self.set_key(i, 'off')
            time.sleep(delay)

    def rainbow_cycle(self, duration=2.0):
        """
        Display a rainbow animation across all keys.

        Args:
            duration: Total duration of the animation
        """
        start = time.monotonic()
        while time.monotonic() - start < duration:
            elapsed = time.monotonic() - start
            for i in range(12):
                # Calculate hue based on position and time
                hue = (i / 12 + elapsed / 2) % 1.0
                color = self._hsv_to_rgb(hue, 1.0, 1.0)
                self.pixels[i] = color
            time.sleep(0.02)

    def _hsv_to_rgb(self, h, s, v):
        """
        Convert HSV to RGB.

        Args:
            h: Hue (0-1)
            s: Saturation (0-1)
            v: Value (0-1)

        Returns:
            RGB tuple (0-255)
        """
        if s == 0.0:
            r = g = b = int(v * 255)
            return (r, g, b)

        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6

        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q

        return (int(r * 255), int(g * 255), int(b * 255))

    def dim_key(self, key_index, factor=0.5):
        """
        Dim a key's current color by a factor.

        Args:
            key_index: Integer 0-11
            factor: Dimming factor (0-1)
        """
        current = self.pixels[key_index]
        dimmed = tuple(int(c * factor) for c in current)
        self.pixels[key_index] = dimmed

    def set_brightness(self, brightness):
        """
        Set global LED brightness.

        Args:
            brightness: Float 0-1
        """
        self.brightness = max(0.0, min(1.0, brightness))
        self.pixels.brightness = self.brightness

    def pulse_key(self, key_index, color, duration=1.0, steps=20):
        """
        Pulse a key (fade in and out).

        Args:
            key_index: Integer 0-11
            color: RGB tuple or color name string
            duration: Total pulse duration
            steps: Number of brightness steps
        """
        if isinstance(color, str):
            color = self.COLORS.get(color, self.COLORS['off'])

        step_time = duration / (steps * 2)

        # Fade in
        for i in range(steps):
            factor = i / steps
            dimmed = tuple(int(c * factor) for c in color)
            self.pixels[key_index] = dimmed
            time.sleep(step_time)

        # Fade out
        for i in range(steps, 0, -1):
            factor = i / steps
            dimmed = tuple(int(c * factor) for c in color)
            self.pixels[key_index] = dimmed
            time.sleep(step_time)

        self.set_key(key_index, 'off')

    def idle_animation(self):
        """
        Play a subtle idle animation (non-blocking single step).
        Call this repeatedly in the menu loop.
        """
        # Gentle wave effect
        current_time = time.monotonic()
        for i in range(12):
            # Create a wave pattern
            brightness = (1 + (0.3 * ((i + current_time * 2) % 3))) / 4
            color = tuple(int(50 * brightness) for _ in range(3))
            self.pixels[i] = color
