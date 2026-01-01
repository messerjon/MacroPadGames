"""
Reaction Timer game for MacroPad.

Tests your reflexes. Wait for the light to turn green, then press as fast as you can.
Measures reaction time in milliseconds. False starts are penalized.
"""

import time
import random
from .base_game import BaseGame


class ReactionTimer(BaseGame):
    """Reaction Timer - Test your reflexes!"""

    NAME = "Reaction"
    DESCRIPTION = "Test your reflexes!"

    # Configuration
    MIN_WAIT_TIME = 1.5           # Minimum wait before green
    MAX_WAIT_TIME = 5.0           # Maximum wait before green
    DISPLAY_TIME = 2.0            # How long to show result
    NUM_ROUNDS = 5                # Number of rounds per game

    # Colors
    READY_COLOR = (255, 255, 0)   # Yellow - get ready
    GO_COLOR = (0, 255, 0)        # Green - press now!
    FALSE_START_COLOR = (255, 0, 0)  # Red - too early

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Reaction Timer game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.round = 0
        self.reaction_times = []
        self.waiting_for_green = False
        self.waiting_for_press = False
        self.green_time = None
        self.wait_until = None
        self.false_start = False

    def start(self):
        """Initialize game."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.clear()
        self.display.show_text("Wait for GREEN", x=15, y=15)
        self.display.show_text("Then press ANY key", x=5, y=30)
        self.display.show_text("as fast as you can!", x=5, y=45)
        time.sleep(2.5)

        self.is_running = True
        print(f"[DEBUG] {self.NAME}.start() complete")
        self._start_round()

    def _start_round(self):
        """Start a new reaction round."""
        self.round += 1
        self.false_start = False
        self.waiting_for_green = True
        self.waiting_for_press = False

        # Show round info
        self.display.clear()
        self.display.show_text(f"Round {self.round}/{self.NUM_ROUNDS}", x=25, y=0)
        self.display.show_text("Get ready...", x=25, y=30)

        # Yellow lights - get ready
        self.leds.set_all(self.READY_COLOR)

        # Set random wait time
        wait_time = random.uniform(self.MIN_WAIT_TIME, self.MAX_WAIT_TIME)
        self.wait_until = time.monotonic() + wait_time

        # Clear any pending key events
        while self.macropad.keys.events.get():
            pass

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        current_time = time.monotonic()

        # Check for key presses
        key_event = self.macropad.keys.events.get()

        if self.waiting_for_green:
            # Check for false start
            if key_event and key_event.pressed:
                self._handle_false_start()
                return True

            # Check if it's time to go green
            if current_time >= self.wait_until:
                self._go_green()

        elif self.waiting_for_press:
            # Waiting for player to press
            if key_event and key_event.pressed:
                reaction_time = (current_time - self.green_time) * 1000  # Convert to ms
                self._handle_reaction(reaction_time)

        # Check for pause/quit
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            if not self.handle_pause():
                return False
            self._start_round()

        return self.is_running

    def _go_green(self):
        """Turn lights green - player should press now!"""
        self.waiting_for_green = False
        self.waiting_for_press = True
        self.green_time = time.monotonic()

        # Green lights - GO!
        self.leds.set_all(self.GO_COLOR)
        self.sound.play_tone(880, 0.1)

        self.display.clear()
        self.display.show_centered_text("GO!", y=20, scale=3)

    def _handle_false_start(self):
        """Handle pressing before green."""
        self.false_start = True
        self.waiting_for_green = False

        # Red lights
        self.leds.set_all(self.FALSE_START_COLOR)
        self.sound.play_wrong()

        self.display.clear()
        self.display.show_centered_text("TOO EARLY!", y=15, scale=2)
        self.display.show_text("Wait for GREEN", x=15, y=45)

        time.sleep(2.0)

        # Add penalty time
        self.reaction_times.append(1000)  # 1 second penalty

        if self.round >= self.NUM_ROUNDS:
            self._handle_game_over()
        else:
            self._start_round()

    def _handle_reaction(self, reaction_time):
        """Handle a reaction time result."""
        self.waiting_for_press = False
        self.reaction_times.append(reaction_time)

        # Flash based on performance
        if reaction_time < 200:
            self.leds.flash_all('cyan', times=3, on_time=0.1, off_time=0.1)
            rating = "AMAZING!"
        elif reaction_time < 300:
            self.leds.flash_all('green', times=2, on_time=0.1, off_time=0.1)
            rating = "Great!"
        elif reaction_time < 400:
            self.leds.set_all('yellow')
            rating = "Good"
        else:
            self.leds.set_all('orange')
            rating = "Slow..."

        self.sound.play_correct()

        # Show result
        self.display.clear()
        self.display.show_centered_text(f"{int(reaction_time)}ms", y=10, scale=2)
        self.display.show_centered_text(rating, y=40)

        time.sleep(self.DISPLAY_TIME)

        if self.round >= self.NUM_ROUNDS:
            self._handle_game_over()
        else:
            self._start_round()

    def _handle_game_over(self):
        """Handle end of game."""
        print(f"[DEBUG] {self.NAME}._handle_game_over()")
        self.is_running = False
        self.game_over = True

        # Calculate average (excluding false starts over 999ms)
        valid_times = [t for t in self.reaction_times if t < 999]
        if valid_times:
            avg_time = sum(valid_times) / len(valid_times)
        else:
            avg_time = 999

        # Score is inverse of time (lower time = higher score)
        self.score = max(0, int(500 - avg_time))

        self.update_high_score()

        self.leds.clear_all()

        self.display.clear()
        self.display.show_centered_text("RESULTS", y=0, scale=2)
        self.display.show_centered_text(f"Avg: {int(avg_time)}ms", y=25)
        self.display.show_centered_text(f"Score: {self.score}", y=40)
        self.display.show_centered_text(f"Best: {self.high_score}", y=52)

        self.wait_for_continue()
        print(f"[DEBUG] {self.NAME}._handle_game_over() complete")

    def handle_key_press(self, key_index):
        """Handle key press - delegated to update loop."""
        pass

    def reset(self):
        """Reset game state."""
        self.round = 0
        self.reaction_times = []
        self.waiting_for_green = False
        self.waiting_for_press = False
        self.green_time = None
        self.wait_until = None
        self.false_start = False
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
