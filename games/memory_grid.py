"""
Memory Grid game for MacroPad.

A pattern of keys lights up briefly, then all lights turn off.
The player must press ALL the keys that were lit (in any order).
Unlike Simon Says, the order doesn't matter - just remembering which keys were part of the pattern.
"""

import time
import random
from .base_game import BaseGame


class MemoryGrid(BaseGame):
    """Memory Grid - Remember the pattern!"""

    NAME = "Memory Grid"
    DESCRIPTION = "Remember the pattern!"

    # Configuration
    INITIAL_PATTERN_SIZE = 3      # Start with 3 keys lit
    MAX_PATTERN_SIZE = 10         # Maximum keys in pattern
    DISPLAY_TIME_BASE = 1.5       # Base time to show pattern
    DISPLAY_TIME_PER_KEY = 0.3    # Additional time per key
    INPUT_TIMEOUT = 10.0          # Time to complete input

    # Colors
    PATTERN_COLOR = (0, 150, 255)  # Cyan-blue for pattern
    CORRECT_COLOR = (0, 255, 0)    # Green for correct
    WRONG_COLOR = (255, 0, 0)      # Red for wrong
    HINT_COLOR = (30, 30, 30)      # Dim for unfound keys (optional hint mode)

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Memory Grid game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.pattern = set()           # Keys in current pattern
        self.found = set()             # Keys player has found
        self.pattern_size = self.INITIAL_PATTERN_SIZE
        self.input_start_time = None
        self.level = 0

    def start(self):
        """Start the game."""
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.show_text("Remember which", x=10, y=30)
        self.display.show_text("keys light up!", x=15, y=42)
        time.sleep(2.0)

        self.is_running = True
        self._start_new_round()

    def _start_new_round(self):
        """Generate and display a new pattern."""
        self.level += 1
        self.found = set()

        # Generate random pattern (CircuitPython doesn't have random.shuffle)
        all_keys = list(range(12))
        self.pattern = set()
        while len(self.pattern) < self.pattern_size:
            key = random.choice(all_keys)
            if key not in self.pattern:
                self.pattern.add(key)

        # Show level info
        self.display.clear()
        self.display.show_text(f"Level: {self.level}", x=0, y=0)
        self.display.show_text(f"Find: {self.pattern_size} keys", x=0, y=50)
        self.display.show_text("Watch...", x=35, y=25)

        time.sleep(0.5)

        # Display pattern
        for key in self.pattern:
            self.leds.set_key(key, self.PATTERN_COLOR)

        # Play tone for memorization aid
        self.sound.play_tone(440, 0.1)

        # Calculate display time based on pattern size
        display_time = self.DISPLAY_TIME_BASE + (self.pattern_size * self.DISPLAY_TIME_PER_KEY)
        time.sleep(display_time)

        # Turn off all lights
        self.leds.clear_all()
        self.sound.play_tone(330, 0.1)  # Signal pattern is hidden

        # Update display for input phase
        self.display.clear()
        self.display.show_text(f"Level: {self.level}", x=0, y=0)
        self.display.show_text("Find them!", x=30, y=25)
        self.display.show_text(f"0 / {self.pattern_size}", x=45, y=50)

        self.input_start_time = time.monotonic()

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        # Check for timeout
        if time.monotonic() - self.input_start_time > self.INPUT_TIMEOUT:
            self._handle_game_over("Time's up!")
            return False

        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            self.handle_key_press(key_event.key_number)

        # Check for pause
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            if not self.handle_pause():
                return False
            # Resume - restart round
            self._start_new_round()

        return self.is_running

    def handle_key_press(self, key_index):
        """Handle key press."""
        if key_index in self.found:
            # Already found this one - brief feedback
            self.leds.flash_key(key_index, self.CORRECT_COLOR, times=1, on_time=0.1, off_time=0)
            return

        if key_index in self.pattern:
            self._handle_correct(key_index)
        else:
            self._handle_wrong(key_index)

    def _handle_correct(self, key_index):
        """Handle correct key found."""
        self.found.add(key_index)

        # Visual/audio feedback
        self.leds.set_key(key_index, self.CORRECT_COLOR)
        self.sound.play_key_tone(key_index)

        # Update display
        self.display.clear()
        self.display.show_text(f"Level: {self.level}", x=0, y=0)
        self.display.show_text("Find them!", x=30, y=25)
        self.display.show_text(f"{len(self.found)} / {self.pattern_size}", x=45, y=50)

        # Check if all found
        if self.found == self.pattern:
            self._handle_level_complete()

    def _handle_wrong(self, key_index):
        """Handle wrong key press."""
        # Show the wrong key
        self.leds.set_key(key_index, self.WRONG_COLOR)
        self.sound.play_wrong()

        time.sleep(0.5)

        # Show the full pattern
        self.leds.clear_all()
        for key in self.pattern:
            if key in self.found:
                self.leds.set_key(key, self.CORRECT_COLOR)
            else:
                self.leds.set_key(key, self.PATTERN_COLOR)
        self.leds.set_key(key_index, self.WRONG_COLOR)

        time.sleep(1.5)

        self._handle_game_over("Wrong key!")

    def _handle_level_complete(self):
        """Handle successful pattern completion."""
        self.score += self.pattern_size * 10

        # Celebration
        self.sound.play_level_up()
        self.leds.flash_all('green', times=2, on_time=0.1, off_time=0.1)

        # Increase difficulty
        if self.pattern_size < self.MAX_PATTERN_SIZE:
            self.pattern_size += 1

        time.sleep(0.5)
        self._start_new_round()

    def _handle_game_over(self, reason):
        """Handle game over."""
        self.is_running = False
        self.game_over = True

        self.update_high_score()

        self.leds.flash_all('red', times=3, on_time=0.2, off_time=0.2)

        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        self.display.show_centered_text(reason, y=28)
        self.display.show_centered_text(f"Level: {self.level}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
        self.wait_for_continue()

    def reset(self):
        """Reset game state."""
        self.pattern = set()
        self.found = set()
        self.pattern_size = self.INITIAL_PATTERN_SIZE
        self.score = 0
        self.level = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
