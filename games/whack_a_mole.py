"""
Whack-a-Mole game for MacroPad.

Multiple "moles" (lit keys) appear and disappear after a short time.
Score points by pressing lit keys before they disappear.
Difficulty increases with more simultaneous moles and shorter visibility.
"""

import time
import random
from .base_game import BaseGame


class WhackAMole(BaseGame):
    """Whack-a-Mole - Hit the moles before they hide!"""

    NAME = "Whack-a-Mole"
    DESCRIPTION = "Hit the moles before they hide!"

    # Timing configuration
    GAME_DURATION = 30.0          # Total game time in seconds
    INITIAL_MOLE_VISIBLE = 1.5    # How long mole stays visible
    MIN_MOLE_VISIBLE = 0.4        # Minimum visibility time
    INITIAL_SPAWN_INTERVAL = 1.0  # Time between mole spawns
    MIN_SPAWN_INTERVAL = 0.3      # Minimum spawn interval

    # Difficulty progression
    DIFFICULTY_INCREASE_INTERVAL = 5.0  # Increase difficulty every N seconds
    MAX_SIMULTANEOUS_MOLES = 4          # Maximum moles at once

    # Scoring
    POINTS_PER_HIT = 10
    MISS_PENALTY = 5              # Points lost for pressing non-mole key

    # Visual
    MOLE_COLOR = (139, 69, 19)    # Brown color for moles
    HIT_COLOR = (0, 255, 0)       # Green flash on hit
    MISS_COLOR = (255, 0, 0)      # Red flash on miss

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Whack-a-Mole game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.active_moles = {}    # {key_index: spawn_time}
        self.game_start_time = None
        self.last_spawn_time = None
        self.current_mole_visible = self.INITIAL_MOLE_VISIBLE
        self.current_spawn_interval = self.INITIAL_SPAWN_INTERVAL
        self.hits = 0
        self.misses = 0

    def start(self):
        """Start the game."""
        self.reset()

        # Show title and instructions
        self.display.show_title(self.NAME)
        time.sleep(0.5)

        # Countdown
        self.do_countdown(3)

        self.game_start_time = time.monotonic()
        self.last_spawn_time = self.game_start_time
        self.is_running = True

        self._update_display()

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        current_time = time.monotonic()
        elapsed = current_time - self.game_start_time

        # Check if game time is up
        if elapsed >= self.GAME_DURATION:
            self._handle_game_over()
            return False

        # Update difficulty based on elapsed time
        self._update_difficulty(elapsed)

        # Spawn new moles
        if current_time - self.last_spawn_time >= self.current_spawn_interval:
            self._spawn_mole()
            self.last_spawn_time = current_time

        # Despawn expired moles
        self._despawn_expired_moles(current_time)

        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            self.handle_key_press(key_event.key_number)

        # Update display periodically
        self._update_display()

        # Check for pause
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            pause_start = time.monotonic()
            if not self.handle_pause():
                return False
            # Adjust timing for pause duration
            pause_duration = time.monotonic() - pause_start
            self.game_start_time += pause_duration
            self.last_spawn_time += pause_duration
            for key in self.active_moles:
                self.active_moles[key] += pause_duration
            # Re-render moles
            for key in self.active_moles:
                self.leds.set_key(key, self.MOLE_COLOR)
            self._update_display()

        return True

    def _spawn_mole(self):
        """Spawn a new mole on a random unoccupied key."""
        if len(self.active_moles) >= self.MAX_SIMULTANEOUS_MOLES:
            return

        available_keys = [k for k in range(12) if k not in self.active_moles]
        if not available_keys:
            return

        key = random.choice(available_keys)
        self.active_moles[key] = time.monotonic()
        self.leds.set_key(key, self.MOLE_COLOR)

    def _despawn_expired_moles(self, current_time):
        """Remove moles that have been visible too long."""
        expired = []
        for key, spawn_time in self.active_moles.items():
            if current_time - spawn_time >= self.current_mole_visible:
                expired.append(key)

        for key in expired:
            del self.active_moles[key]
            self.leds.set_key(key, 'off')
            self.misses += 1  # Missed mole counts as miss

    def handle_key_press(self, key_index):
        """Handle key press."""
        if key_index in self.active_moles:
            self._handle_hit(key_index)
        else:
            self._handle_miss(key_index)

    def _handle_hit(self, key_index):
        """Handle successful mole hit."""
        del self.active_moles[key_index]
        self.hits += 1
        self.score += self.POINTS_PER_HIT

        # Visual/audio feedback
        self.leds.set_key(key_index, self.HIT_COLOR)
        self.sound.play_correct()

        # Brief delay then turn off
        time.sleep(0.05)
        self.leds.set_key(key_index, 'off')

    def _handle_miss(self, key_index):
        """Handle miss (pressing non-mole key)."""
        self.misses += 1
        self.score = max(0, self.score - self.MISS_PENALTY)

        # Visual/audio feedback
        self.leds.flash_key(key_index, self.MISS_COLOR, times=1, on_time=0.1, off_time=0)
        self.sound.play_tone(200, 0.1)  # Low buzz

    def _update_difficulty(self, elapsed):
        """Increase difficulty over time."""
        difficulty_level = int(elapsed / self.DIFFICULTY_INCREASE_INTERVAL)

        # Decrease mole visibility time
        self.current_mole_visible = max(
            self.MIN_MOLE_VISIBLE,
            self.INITIAL_MOLE_VISIBLE - (difficulty_level * 0.15)
        )

        # Decrease spawn interval (more frequent moles)
        self.current_spawn_interval = max(
            self.MIN_SPAWN_INTERVAL,
            self.INITIAL_SPAWN_INTERVAL - (difficulty_level * 0.1)
        )

    def _update_display(self):
        """Update the OLED display."""
        elapsed = time.monotonic() - self.game_start_time
        remaining = max(0, self.GAME_DURATION - elapsed)

        self.display.clear()
        self.display.show_text(f"Score: {self.score}", x=0, y=0)
        self.display.show_text(f"Time: {int(remaining)}s", x=70, y=0)
        self.display.show_text(f"Hits: {self.hits}", x=0, y=50)

    def _handle_game_over(self):
        """Handle end of game."""
        self.is_running = False
        self.game_over = True

        self.update_high_score()

        # Clear remaining moles
        self.leds.clear_all()

        # Victory animation
        self.sound.play_level_up()
        self.leds.sweep_animation('green')

        # Show results
        self.display.clear()
        self.display.show_centered_text("TIME'S UP!", y=5, scale=2)
        self.display.show_centered_text(f"Score: {self.score}", y=30)
        self.display.show_centered_text(f"Hits: {self.hits}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
        self.wait_for_continue()

    def reset(self):
        """Reset game state."""
        self.active_moles = {}
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.current_mole_visible = self.INITIAL_MOLE_VISIBLE
        self.current_spawn_interval = self.INITIAL_SPAWN_INTERVAL
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
