"""
Simon Says game for MacroPad.

Classic memory game. The game plays an increasingly long sequence of colors/keys.
The player must repeat the sequence exactly. Each successful round adds one more step.
"""

import time
import random
from .base_game import BaseGame


class SimonSays(BaseGame):
    """Simon Says - Repeat the sequence!"""

    NAME = "Simon Says"
    DESCRIPTION = "Repeat the sequence!"

    # Configuration
    SEQUENCE_DISPLAY_TIME = 0.5   # Time each key is shown
    SEQUENCE_GAP_TIME = 0.2       # Gap between sequence items
    INPUT_TIMEOUT = 5.0           # Time allowed per input
    SPEED_INCREASE_INTERVAL = 5   # Speed up every N levels
    MIN_DISPLAY_TIME = 0.2        # Fastest display time

    # The four Simon colors (using 4 specific keys in a 2x2 pattern)
    SIMON_KEYS = [0, 1, 3, 4]     # Top-left 2x2 grid
    SIMON_COLORS = {
        0: ('red', (255, 0, 0)),
        1: ('blue', (0, 0, 255)),
        3: ('green', (0, 255, 0)),
        4: ('yellow', (255, 255, 0)),
    }

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Simon Says game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.sequence = []
        self.player_position = 0
        self.current_display_time = self.SEQUENCE_DISPLAY_TIME
        self.waiting_for_input = False
        self.input_start_time = None

    def start(self):
        """Initialize game."""
        self.reset()

        # Show title
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(1.0)

        # Highlight the four Simon keys to show which ones to use
        for key in self.SIMON_KEYS:
            color_name, color_rgb = self.SIMON_COLORS[key]
            self.leds.set_key(key, color_rgb)
        time.sleep(1.5)
        self.leds.clear_all()

        self.is_running = True
        self._add_to_sequence()
        self._play_sequence()

    def _add_to_sequence(self):
        """Add a random step to the sequence."""
        new_key = random.choice(self.SIMON_KEYS)
        self.sequence.append(new_key)

    def _play_sequence(self):
        """Display the current sequence to the player."""
        self.waiting_for_input = False

        # Show level
        level = len(self.sequence)
        self.display.clear()
        self.display.show_text(f"Level: {level}", x=0, y=0)
        self.display.show_text("Watch...", x=30, y=30)

        time.sleep(0.5)

        # Play each item in sequence
        for key in self.sequence:
            color_name, color_rgb = self.SIMON_COLORS[key]

            # Light up key and play tone
            self.leds.set_key(key, color_rgb)
            self.sound.play_key_tone(key)
            time.sleep(self.current_display_time)

            # Turn off
            self.leds.set_key(key, 'off')
            time.sleep(self.SEQUENCE_GAP_TIME)

        # Ready for player input
        self.player_position = 0
        self.waiting_for_input = True
        self.input_start_time = time.monotonic()

        # Show dim colors on Simon keys as hints
        for key in self.SIMON_KEYS:
            color_name, color_rgb = self.SIMON_COLORS[key]
            dim_color = tuple(c // 4 for c in color_rgb)
            self.leds.set_key(key, dim_color)

        self.display.clear()
        self.display.show_text(f"Level: {level}", x=0, y=0)
        self.display.show_text("Your turn!", x=25, y=30)

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        if self.waiting_for_input:
            # Check for timeout
            if time.monotonic() - self.input_start_time > self.INPUT_TIMEOUT:
                self._handle_game_over("Time's up!")
                return False

            # Check for key presses
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self.handle_key_press(key_event.key_number)

        # Check for encoder press (pause)
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            if not self.handle_pause():
                return False
            # Resume - replay current sequence
            self._play_sequence()

        return self.is_running

    def handle_key_press(self, key_index):
        """Process player input."""
        if not self.waiting_for_input:
            return

        # Only accept Simon keys
        if key_index not in self.SIMON_KEYS:
            # Flash to indicate invalid key, but don't penalize
            self.leds.flash_key(key_index, 'white', times=1, on_time=0.1, off_time=0)
            return

        expected_key = self.sequence[self.player_position]

        if key_index == expected_key:
            self._handle_correct_input(key_index)
        else:
            self._handle_wrong_input(key_index, expected_key)

    def _handle_correct_input(self, key_index):
        """Handle correct key press."""
        # Visual/audio feedback
        color_name, color_rgb = self.SIMON_COLORS[key_index]
        self.leds.set_key(key_index, color_rgb)
        self.sound.play_key_tone(key_index)
        time.sleep(0.2)

        # Dim back
        dim_color = tuple(c // 4 for c in color_rgb)
        self.leds.set_key(key_index, dim_color)

        self.player_position += 1
        self.input_start_time = time.monotonic()  # Reset timeout

        # Check if sequence complete
        if self.player_position >= len(self.sequence):
            self._handle_level_complete()

    def _handle_wrong_input(self, pressed_key, expected_key):
        """Handle wrong key press."""
        # Show what was pressed (red) vs what was expected (green)
        self.leds.clear_all()
        self.leds.set_key(pressed_key, 'red')
        self.leds.set_key(expected_key, 'green')
        self.sound.play_wrong()
        time.sleep(1.5)

        self._handle_game_over("Wrong key!")

    def _handle_level_complete(self):
        """Handle successful completion of a level."""
        self.score = len(self.sequence)

        # Celebration animation
        self.leds.clear_all()
        self.sound.play_level_up()
        self.leds.flash_all('green', times=2, on_time=0.1, off_time=0.1)

        # Speed up every N levels
        if self.score % self.SPEED_INCREASE_INTERVAL == 0:
            self.current_display_time = max(
                self.MIN_DISPLAY_TIME,
                self.current_display_time * 0.85
            )

        # Add next step and continue
        time.sleep(0.5)
        self._add_to_sequence()
        self._play_sequence()

    def _handle_game_over(self, reason):
        """Handle game over."""
        self.is_running = False
        self.game_over = True

        self.update_high_score()

        self.leds.flash_all('red', times=3, on_time=0.2, off_time=0.2)

        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        self.display.show_centered_text(reason, y=28)
        self.display.show_centered_text(f"Level: {self.score}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
        self.wait_for_continue()

    def reset(self):
        """Reset for new game."""
        self.sequence = []
        self.player_position = 0
        self.current_display_time = self.SEQUENCE_DISPLAY_TIME
        self.waiting_for_input = False
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
