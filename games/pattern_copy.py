"""
Pattern Copy game for MacroPad.

A pattern is shown briefly. Copy it exactly by pressing the same keys.
Unlike Memory Grid, you must match the EXACT positions, not just find them.
Speed increases with each level.
"""

import time
import random
from .base_game import BaseGame


class PatternCopy(BaseGame):
    """Pattern Copy - Copy the pattern exactly!"""

    NAME = "Pattern Copy"
    DESCRIPTION = "Copy the pattern!"

    # Configuration
    INITIAL_PATTERN_SIZE = 3
    MAX_PATTERN_SIZE = 8
    INITIAL_SHOW_TIME = 2.0       # How long to show pattern
    MIN_SHOW_TIME = 0.5           # Minimum show time
    SHOW_TIME_DECREASE = 0.15     # Decrease per level
    INPUT_TIMEOUT = 10.0          # Time to complete input

    # Colors
    PATTERN_COLOR = (0, 200, 255)  # Cyan for pattern
    INPUT_COLOR = (255, 200, 0)    # Yellow for input
    CORRECT_COLOR = (0, 255, 0)    # Green for correct
    WRONG_COLOR = (255, 0, 0)      # Red for wrong

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Pattern Copy game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.pattern = []
        self.player_input = []
        self.pattern_size = self.INITIAL_PATTERN_SIZE
        self.show_time = self.INITIAL_SHOW_TIME
        self.input_start_time = None
        self.level = 0
        self.accepting_input = False

    def start(self):
        """Initialize game."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.clear()
        self.display.show_text("Watch the pattern", x=10, y=20)
        self.display.show_text("Then copy it!", x=25, y=35)
        time.sleep(2.0)

        self.is_running = True
        print(f"[DEBUG] {self.NAME}.start() complete")
        self._start_new_round()

    def _start_new_round(self):
        """Start a new round with a new pattern."""
        self.level += 1
        self.player_input = []
        self.accepting_input = False

        # Generate random pattern
        self.pattern = []
        available = list(range(12))
        for _ in range(self.pattern_size):
            if available:
                key = random.choice(available)
                available.remove(key)
                self.pattern.append(key)

        # Show level info
        self.display.clear()
        self.display.show_text(f"Level {self.level}", x=40, y=0)
        self.display.show_text(f"Pattern: {self.pattern_size} keys", x=10, y=25)
        self.display.show_text("Watch closely!", x=20, y=45)

        time.sleep(1.0)

        # Show pattern
        self.display.clear()
        self.display.show_text(f"Level {self.level}", x=40, y=0)
        self.display.show_centered_text("MEMORIZE!", y=30)

        self.leds.clear_all()
        for key in self.pattern:
            self.leds.set_key(key, self.PATTERN_COLOR)

        self.sound.play_tone(660, 0.1)
        time.sleep(self.show_time)

        # Hide pattern
        self.leds.clear_all()
        self.sound.play_tone(440, 0.1)

        # Ready for input
        self.display.clear()
        self.display.show_text(f"Level {self.level}", x=40, y=0)
        self.display.show_centered_text("Your turn!", y=25)
        self.display.show_text(f"0/{self.pattern_size}", x=50, y=50)

        self.input_start_time = time.monotonic()
        self.accepting_input = True

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        if self.accepting_input:
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
            self._start_new_round()

        return self.is_running

    def handle_key_press(self, key_index):
        """Handle key press during input phase."""
        if not self.accepting_input:
            return

        if key_index in self.player_input:
            # Already pressed this key
            self.leds.flash_key(key_index, 'white', times=1, on_time=0.1, off_time=0)
            return

        self.player_input.append(key_index)

        # Check if this key is correct
        if key_index in self.pattern:
            # Correct key
            self.leds.set_key(key_index, self.CORRECT_COLOR)
            self.sound.play_tone(550, 0.05)

            # Update display
            self.display.clear()
            self.display.show_text(f"Level {self.level}", x=40, y=0)
            self.display.show_centered_text("Your turn!", y=25)
            self.display.show_text(f"{len([k for k in self.player_input if k in self.pattern])}/{self.pattern_size}", x=50, y=50)

            # Check if all found
            correct_count = len([k for k in self.player_input if k in self.pattern])
            if correct_count >= self.pattern_size:
                self._handle_round_complete()
        else:
            # Wrong key
            self._handle_wrong_key(key_index)

    def _handle_wrong_key(self, key_index):
        """Handle wrong key press."""
        self.accepting_input = False

        # Show what was wrong
        self.leds.set_key(key_index, self.WRONG_COLOR)
        self.sound.play_wrong()
        time.sleep(0.5)

        # Show correct pattern
        self.leds.clear_all()
        for key in self.pattern:
            self.leds.set_key(key, self.PATTERN_COLOR)
        self.leds.set_key(key_index, self.WRONG_COLOR)

        time.sleep(1.5)
        self._handle_game_over("Wrong key!")

    def _handle_round_complete(self):
        """Handle successful round completion."""
        self.accepting_input = False
        self.score += self.pattern_size * 10

        # Success animation
        self.sound.play_correct()
        self.leds.flash_all('green', times=2, on_time=0.1, off_time=0.1)

        # Increase difficulty
        if self.pattern_size < self.MAX_PATTERN_SIZE:
            self.pattern_size += 1
        self.show_time = max(self.MIN_SHOW_TIME, self.show_time - self.SHOW_TIME_DECREASE)

        time.sleep(0.5)
        self._start_new_round()

    def _handle_game_over(self, reason):
        """Handle game over."""
        print(f"[DEBUG] {self.NAME}._handle_game_over()")
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
        print(f"[DEBUG] {self.NAME}._handle_game_over() complete")

    def reset(self):
        """Reset game state."""
        self.pattern = []
        self.player_input = []
        self.pattern_size = self.INITIAL_PATTERN_SIZE
        self.show_time = self.INITIAL_SHOW_TIME
        self.level = 0
        self.score = 0
        self.accepting_input = False
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
