"""
Hot Potato game for MacroPad.

A "hot potato" (lit key) bounces around the grid.
Press it to pass it to a random adjacent key.
When the timer stops, don't be holding it!
Survive rounds to score points.
"""

import time
import random
from .base_game import BaseGame


class HotPotato(BaseGame):
    """Hot Potato - Don't hold it when the music stops!"""

    NAME = "Hot Potato"
    DESCRIPTION = "Pass it quick!"

    # Adjacency map for bouncing
    ADJACENCY = {
        0: [1, 3],
        1: [0, 2, 4],
        2: [1, 5],
        3: [0, 4, 6],
        4: [1, 3, 5, 7],
        5: [2, 4, 8],
        6: [3, 7, 9],
        7: [4, 6, 8, 10],
        8: [5, 7, 11],
        9: [6, 10],
        10: [7, 9, 11],
        11: [8, 10],
    }

    # Configuration
    MIN_ROUND_TIME = 2.0          # Minimum time before explosion
    MAX_ROUND_TIME = 6.0          # Maximum time before explosion
    INITIAL_MOVE_INTERVAL = 0.8   # How fast potato moves initially
    MIN_MOVE_INTERVAL = 0.2       # Fastest potato movement
    WARNING_TIME = 1.0            # Time before explosion to start warning
    NUM_ROUNDS = 10               # Rounds per game

    # Colors
    POTATO_COLOR = (255, 100, 0)   # Orange
    WARNING_COLOR = (255, 0, 0)    # Red when about to explode
    SAFE_COLOR = (0, 255, 0)       # Green when safe
    EXPLODE_COLOR = (255, 255, 255)  # White flash on explosion

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Hot Potato game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.potato_key = 0
        self.round = 0
        self.round_end_time = 0
        self.last_move_time = 0
        self.move_interval = self.INITIAL_MOVE_INTERVAL
        self.round_active = False
        self.survived = 0

    def start(self):
        """Initialize game."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.clear()
        self.display.show_text("Pass the potato!", x=15, y=15)
        self.display.show_text("Press it to pass", x=15, y=30)
        self.display.show_text("Don't hold when", x=15, y=45)
        time.sleep(2.0)
        self.display.clear()
        self.display.show_text("it EXPLODES!", x=25, y=25)
        time.sleep(1.5)

        self.is_running = True
        print(f"[DEBUG] {self.NAME}.start() complete")
        self._start_round()

    def _start_round(self):
        """Start a new round."""
        self.round += 1
        self.round_active = True

        # Random starting position
        self.potato_key = random.randint(0, 11)

        # Random round duration
        round_duration = random.uniform(self.MIN_ROUND_TIME, self.MAX_ROUND_TIME)
        self.round_end_time = time.monotonic() + round_duration
        self.last_move_time = time.monotonic()

        # Show round info
        self.display.clear()
        self.display.show_text(f"Round {self.round}/{self.NUM_ROUNDS}", x=20, y=0)
        self.display.show_text("PASS IT!", x=35, y=30)
        self.display.show_text(f"Survived: {self.survived}", x=25, y=50)

        # Light up potato
        self.leds.clear_all()
        self.leds.set_key(self.potato_key, self.POTATO_COLOR)

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        current_time = time.monotonic()

        if self.round_active:
            time_remaining = self.round_end_time - current_time

            # Check if round ended (explosion!)
            if time_remaining <= 0:
                self._handle_explosion()
                return self.is_running

            # Warning phase - potato flashes faster
            if time_remaining < self.WARNING_TIME:
                # Flash between potato and warning color
                flash_rate = 0.1
                if int(current_time / flash_rate) % 2 == 0:
                    self.leds.set_key(self.potato_key, self.WARNING_COLOR)
                else:
                    self.leds.set_key(self.potato_key, self.POTATO_COLOR)
                # Beeping gets faster
                if int(current_time * 10) % 3 == 0:
                    self.sound.play_tone(880, 0.02)

            # Auto-move potato if player doesn't pass it
            elif current_time - self.last_move_time >= self.move_interval:
                self._auto_move_potato()

        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed and self.round_active:
            self.handle_key_press(key_event.key_number)

        # Check for pause
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            if not self.handle_pause():
                return False
            self._start_round()

        return self.is_running

    def handle_key_press(self, key_index):
        """Handle key press - pass the potato."""
        if key_index == self.potato_key:
            # Pressed the potato - pass it!
            self._pass_potato()
        else:
            # Wrong key - brief feedback
            self.leds.flash_key(key_index, 'white', times=1, on_time=0.05, off_time=0)

    def _pass_potato(self):
        """Pass the potato to an adjacent key."""
        # Turn off current position
        self.leds.set_key(self.potato_key, 'off')

        # Move to random adjacent key
        neighbors = self.ADJACENCY[self.potato_key]
        self.potato_key = random.choice(neighbors)

        # Light up new position
        self.leds.set_key(self.potato_key, self.POTATO_COLOR)

        # Sound feedback
        self.sound.play_tone(440, 0.03)

        # Reset auto-move timer
        self.last_move_time = time.monotonic()

    def _auto_move_potato(self):
        """Automatically move potato (if player doesn't pass it)."""
        self._pass_potato()

    def _handle_explosion(self):
        """Handle the potato exploding."""
        self.round_active = False

        # Explosion animation
        self.leds.set_all(self.EXPLODE_COLOR)
        self.sound.play_tone(200, 0.3)
        time.sleep(0.3)
        self.leds.set_all(self.WARNING_COLOR)
        self.sound.play_tone(150, 0.3)
        time.sleep(0.3)

        # Check if player was holding it
        # For single player, we check if potato moved recently (player was actively playing)
        # If last_move was very recent, player was "holding" it
        time_since_pass = time.monotonic() - self.last_move_time

        if time_since_pass < 0.3:
            # Player was "holding" the potato when it exploded
            self._handle_caught()
        else:
            # Player successfully passed it
            self._handle_safe()

    def _handle_safe(self):
        """Handle surviving a round."""
        self.survived += 1
        self.score += 10

        self.leds.set_all(self.SAFE_COLOR)
        self.sound.play_correct()

        self.display.clear()
        self.display.show_centered_text("SAFE!", y=20, scale=2)

        time.sleep(1.5)

        # Speed up for next round
        self.move_interval = max(self.MIN_MOVE_INTERVAL, self.move_interval - 0.05)

        if self.round >= self.NUM_ROUNDS:
            self._handle_victory()
        else:
            self._start_round()

    def _handle_caught(self):
        """Handle being caught with the potato."""
        self.leds.flash_all('red', times=3, on_time=0.2, off_time=0.2)
        self.sound.play_wrong()

        self.display.clear()
        self.display.show_centered_text("BOOM!", y=15, scale=2)
        self.display.show_text("You got caught!", x=15, y=45)

        time.sleep(2.0)
        self._handle_game_over()

    def _handle_victory(self):
        """Handle completing all rounds."""
        self.is_running = False
        self.game_over = True
        self.score += self.survived * 20  # Bonus

        self.update_high_score()

        self.sound.play_level_up()
        self.leds.rainbow_cycle(duration=2.0)

        self.display.clear()
        self.display.show_centered_text("WINNER!", y=5, scale=2)
        self.display.show_centered_text(f"Survived: {self.survived}", y=30)
        self.display.show_centered_text(f"Score: {self.score}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)

        self.wait_for_continue()

    def _handle_game_over(self):
        """Handle game over."""
        print(f"[DEBUG] {self.NAME}._handle_game_over()")
        self.is_running = False
        self.game_over = True

        self.update_high_score()

        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        self.display.show_centered_text(f"Survived: {self.survived}/{self.NUM_ROUNDS}", y=28)
        self.display.show_centered_text(f"Score: {self.score}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)

        self.wait_for_continue()
        print(f"[DEBUG] {self.NAME}._handle_game_over() complete")

    def reset(self):
        """Reset game state."""
        self.potato_key = 0
        self.round = 0
        self.survived = 0
        self.move_interval = self.INITIAL_MOVE_INTERVAL
        self.round_active = False
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
