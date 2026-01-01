"""
Speed Chase game for MacroPad.

A single random key lights up. Press it before time runs out.
Each success makes the next key light up faster.
Game ends on wrong press or timeout.
"""

import time
import random
from .base_game import BaseGame


class SpeedChase(BaseGame):
    """Speed Chase - Press the lit key before time runs out!"""

    NAME = "Speed Chase"
    DESCRIPTION = "Press the lit key before time runs out!"

    # Timing configuration (in seconds)
    INITIAL_TIME_LIMIT = 2.0      # Time to press first key
    MINIMUM_TIME_LIMIT = 0.3      # Fastest possible time limit
    TIME_DECREASE_FACTOR = 0.92   # Multiply time limit by this each round
    FEEDBACK_DURATION = 0.15      # How long to show correct feedback

    # Scoring
    BASE_POINTS = 10
    SPEED_BONUS_MULTIPLIER = 2    # Bonus points for fast responses

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Speed Chase game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.current_target = None
        self.target_color = None
        self.time_limit = self.INITIAL_TIME_LIMIT
        self.target_start_time = None
        self.round_number = 0

    def start(self):
        """Initialize game state and show countdown."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()
        self.display.show_title(self.NAME)
        time.sleep(0.5)

        # 3-2-1 countdown
        self.do_countdown(3)

        self.is_running = True
        print(f"[DEBUG] {self.NAME}.start() complete, is_running={self.is_running}")
        self._show_next_target()

    def _show_next_target(self):
        """Select and display a new random target key."""
        # Select random key (avoid same key twice in a row)
        available_keys = [k for k in range(12) if k != self.current_target]
        self.current_target = random.choice(available_keys)

        # Select random color
        self.target_color, color_name = self.leds.get_random_color()

        # Light up the target
        self.leds.clear_all()
        self.leds.set_key(self.current_target, self.target_color)

        # Record start time for timeout tracking
        self.target_start_time = time.monotonic()
        self.round_number += 1

        # Update display
        self.display.clear()
        self.display.show_text(f"Round: {self.round_number}", x=0, y=0)
        self.display.show_score(self.score)

    def update(self):
        """Main game loop - check for timeout and inputs."""
        if not self.is_running:
            print(f"[DEBUG] {self.NAME}.update() - is_running=False, returning False")
            return False

        # Check for timeout
        elapsed = time.monotonic() - self.target_start_time
        if elapsed >= self.time_limit:
            print(f"[DEBUG] {self.NAME}.update() - timeout, calling _handle_timeout()")
            self._handle_timeout()
            return False

        # Check for key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            print(f"[DEBUG] {self.NAME}.update() - key {key_event.key_number} pressed")
            self.handle_key_press(key_event.key_number)

        # Check for encoder press (pause/quit)
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            print(f"[DEBUG] {self.NAME}.update() - encoder pressed, calling handle_pause()")
            if not self.handle_pause():
                print(f"[DEBUG] {self.NAME}.update() - pause returned False, exiting")
                return False
            # Resume - re-show the current target with fresh timing
            self._show_next_target()

        return self.is_running

    def handle_key_press(self, key_index):
        """Process a key press."""
        if key_index == self.current_target:
            self._handle_correct_press()
        else:
            self._handle_wrong_press(key_index)

    def _handle_correct_press(self):
        """Handle correct key press."""
        # Calculate score with speed bonus
        elapsed = time.monotonic() - self.target_start_time
        time_bonus = int((1 - elapsed / self.time_limit) * self.BASE_POINTS * self.SPEED_BONUS_MULTIPLIER)
        points = self.BASE_POINTS + max(0, time_bonus)
        self.score += points

        # Play success feedback
        self.sound.play_correct()

        # Brief visual feedback - flash the key green
        self.leds.flash_key(self.current_target, 'green', times=2, on_time=0.05, off_time=0.05)

        # Decrease time limit for next round (increase difficulty)
        self.time_limit = max(self.MINIMUM_TIME_LIMIT, self.time_limit * self.TIME_DECREASE_FACTOR)

        # Show next target
        self._show_next_target()

    def _handle_wrong_press(self, pressed_key):
        """Handle wrong key press - game over."""
        print(f"[DEBUG] {self.NAME}._handle_wrong_press(key={pressed_key})")
        self.is_running = False
        self.game_over = True
        print(f"[DEBUG] {self.NAME} set is_running=False, game_over=True")

        # Visual feedback - flash wrong key red, correct key green
        self.leds.clear_all()
        self.leds.set_key(pressed_key, 'red')
        self.leds.set_key(self.current_target, 'green')
        self.sound.play_wrong()
        time.sleep(1.0)

        # Flash all red for game over
        self.leds.flash_all('red', times=3, on_time=0.2, off_time=0.2)

        # Show game over screen
        print(f"[DEBUG] {self.NAME} calling show_game_over_screen()")
        self.show_game_over_screen("Wrong key!")
        print(f"[DEBUG] {self.NAME}._handle_wrong_press() complete")

    def _handle_timeout(self):
        """Handle timeout - game over."""
        print(f"[DEBUG] {self.NAME}._handle_timeout()")
        self.is_running = False
        self.game_over = True
        print(f"[DEBUG] {self.NAME} set is_running=False, game_over=True")

        # Visual feedback - flash target key indicating missed
        self.leds.flash_key(self.current_target, 'red', times=5, on_time=0.1, off_time=0.1)
        self.sound.play_wrong()

        # Show game over screen
        print(f"[DEBUG] {self.NAME} calling show_game_over_screen()")
        self.show_game_over_screen("Time's up!")
        print(f"[DEBUG] {self.NAME}._handle_timeout() complete")

    def reset(self):
        """Reset game state for new game."""
        self.score = 0
        self.current_target = None
        self.target_color = None
        self.time_limit = self.INITIAL_TIME_LIMIT
        self.target_start_time = None
        self.round_number = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
