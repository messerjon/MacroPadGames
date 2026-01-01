"""
Lights Out game for MacroPad.

Classic puzzle game. All keys start lit (or in a random pattern).
Pressing a key toggles that key AND its adjacent neighbors (up, down, left, right).
The goal is to turn all lights OFF.
"""

import time
import random
from .base_game import BaseGame


class LightsOut(BaseGame):
    """Lights Out - Turn off all the lights!"""

    NAME = "Lights Out"
    DESCRIPTION = "Turn off all the lights!"

    # Adjacency map for 3x4 grid
    # Key Layout:
    # 0  1  2
    # 3  4  5
    # 6  7  8
    # 9  10 11
    ADJACENCY = {
        0: [0, 1, 3],
        1: [0, 1, 2, 4],
        2: [1, 2, 5],
        3: [0, 3, 4, 6],
        4: [1, 3, 4, 5, 7],
        5: [2, 4, 5, 8],
        6: [3, 6, 7, 9],
        7: [4, 6, 7, 8, 10],
        8: [5, 7, 8, 11],
        9: [6, 9, 10],
        10: [7, 9, 10, 11],
        11: [8, 10, 11],
    }

    # Configuration
    INITIAL_RANDOM_MOVES = 5      # Random moves to scramble starting position
    MAX_RANDOM_MOVES = 15         # Maximum scramble for harder levels

    # Colors
    LIGHT_ON = (255, 200, 50)     # Warm yellow for "on"
    LIGHT_OFF = (0, 0, 0)         # Off
    TOGGLE_FLASH = (255, 255, 255)  # White flash when toggling

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Lights Out game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.lights = [False] * 12  # True = on, False = off
        self.move_count = 0
        self.level = 1
        self.random_moves = self.INITIAL_RANDOM_MOVES
        self._last_encoder = None

    def start(self):
        """Start the game."""
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.show_text("Press a key to", x=10, y=25)
        self.display.show_text("toggle + neighbors", x=5, y=37)
        self.display.show_text("Goal: All off!", x=15, y=52)
        time.sleep(3.0)

        self.is_running = True
        self._last_encoder = self.macropad.encoder
        self._generate_puzzle()

    def _generate_puzzle(self):
        """Generate a solvable puzzle by working backwards."""
        # Start with all lights off
        self.lights = [False] * 12

        # Apply random moves to create puzzle
        # This guarantees the puzzle is solvable
        for _ in range(self.random_moves):
            key = random.randint(0, 11)
            self._toggle_lights(key, animate=False)

        # Make sure at least some lights are on
        while sum(self.lights) == 0:
            key = random.randint(0, 11)
            self._toggle_lights(key, animate=False)

        self.move_count = 0
        self._update_display()
        self._render_lights()

    def _toggle_lights(self, key_index, animate=True):
        """Toggle the pressed key and its neighbors."""
        affected_keys = self.ADJACENCY[key_index]

        if animate:
            # Flash affected keys
            for key in affected_keys:
                self.leds.set_key(key, self.TOGGLE_FLASH)
            self.sound.play_tone(440, 0.05)
            time.sleep(0.05)

        # Toggle each affected key
        for key in affected_keys:
            self.lights[key] = not self.lights[key]

        if animate:
            self._render_lights()

    def _render_lights(self):
        """Update LED display based on current light state."""
        for i in range(12):
            if self.lights[i]:
                self.leds.set_key(i, self.LIGHT_ON)
            else:
                self.leds.set_key(i, self.LIGHT_OFF)

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            self.handle_key_press(key_event.key_number)

        # Check for encoder actions
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            return self._handle_pause_menu()

        # Encoder rotation could reset puzzle
        encoder_delta = self.macropad.encoder - self._last_encoder
        if encoder_delta != 0:
            self._last_encoder = self.macropad.encoder
            # Could implement hint or undo functionality here

        return self.is_running

    def handle_key_press(self, key_index):
        """Handle key press - toggle lights."""
        self._toggle_lights(key_index)
        self.move_count += 1
        self._update_display()

        # Check for win condition
        if not any(self.lights):
            self._handle_victory()

    def _update_display(self):
        """Update OLED display."""
        self.display.clear()
        self.display.show_text(f"Level: {self.level}", x=0, y=0)
        self.display.show_text(f"Moves: {self.move_count}", x=0, y=50)

        lights_on = sum(self.lights)
        self.display.show_text(f"Lit: {lights_on}/12", x=65, y=0)

    def _handle_victory(self):
        """Handle puzzle solved."""
        # Calculate score (fewer moves = higher score)
        base_score = 100
        move_penalty = self.move_count * 2
        level_bonus = self.level * 20
        self.score = max(10, base_score - move_penalty + level_bonus)

        self.update_high_score()

        # Victory animation
        self.sound.play_level_up()
        self.leds.sweep_animation('green')

        # Show results
        self.display.clear()
        self.display.show_centered_text("SOLVED!", y=5, scale=2)
        self.display.show_centered_text(f"Moves: {self.move_count}", y=30)
        self.display.show_centered_text(f"Score: {self.score}", y=42)

        time.sleep(2.0)

        # Prompt for next level or menu
        self.display.show_text("Key: Next level", x=10, y=52)

        # Wait for input
        while True:
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self._next_level()
                return

            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                self.is_running = False
                self.game_over = True
                return

    def _next_level(self):
        """Advance to next level."""
        self.level += 1
        self.random_moves = min(self.MAX_RANDOM_MOVES, self.random_moves + 1)
        self._generate_puzzle()

    def _handle_pause_menu(self):
        """Handle pause - show options."""
        self.display.clear()
        self.display.show_centered_text("PAUSED", y=5, scale=2)
        self.display.show_text("Encoder: Quit", x=20, y=30)
        self.display.show_text("Any key: Resume", x=15, y=42)

        self.leds.clear_all()

        while True:
            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                return False  # Quit

            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self._update_display()
                self._render_lights()
                return True  # Resume

    def reset(self):
        """Reset game state."""
        self.lights = [False] * 12
        self.move_count = 0
        self.level = 1
        self.random_moves = self.INITIAL_RANDOM_MOVES
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
