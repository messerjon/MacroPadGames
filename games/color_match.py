"""
Color Match game for MacroPad.

All keys start off. A target color is shown on the display.
After countdown, random colors appear on all keys.
Player must quickly press all keys matching the target color.
Speed increases each round. Game ends when time runs out.
"""

import time
import random
from .base_game import BaseGame


class ColorMatch(BaseGame):
    """Color Match - Find all keys matching the target color!"""

    NAME = "Color Match"
    DESCRIPTION = "Find the matching colors!"

    # Configuration
    GAME_DURATION = 30.0          # Total game time in seconds
    INITIAL_ROUND_TIME = 5.0      # Time for first round
    MIN_ROUND_TIME = 1.5          # Fastest round time
    ROUND_TIME_DECREASE = 0.3     # Decrease per level
    COUNTDOWN_TIME = 3            # Countdown before colors appear

    # Scoring
    POINTS_PER_CORRECT = 10
    POINTS_PER_WRONG = -5

    # Colors used in the game
    COLORS = [
        ('RED', (255, 0, 0)),
        ('GREEN', (0, 255, 0)),
        ('BLUE', (0, 0, 255)),
        ('YELLOW', (255, 255, 0)),
        ('CYAN', (0, 255, 255)),
        ('PURPLE', (128, 0, 255)),
    ]

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Color Match game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.target_color_index = 0
        self.key_colors = []          # Color index for each key
        self.matching_keys = set()    # Keys that match target
        self.found_keys = set()       # Keys player has found
        self.round_time = self.INITIAL_ROUND_TIME
        self.round_start_time = None
        self.game_start_time = None
        self.level = 0
        self.in_round = False
        self.correct_hits = 0
        self.wrong_hits = 0

    def start(self):
        """Initialize game."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.clear()
        self.display.show_text("Find all keys", x=15, y=20)
        self.display.show_text("matching the color!", x=5, y=35)
        time.sleep(2.0)

        self.game_start_time = time.monotonic()
        self.is_running = True
        print(f"[DEBUG] {self.NAME}.start() complete, starting first round")
        self._start_new_round()

    def _start_new_round(self):
        """Start a new round with a new target color."""
        self.level += 1
        self.found_keys = set()
        self.in_round = False

        # All keys off
        self.leds.clear_all()

        # Pick a random target color
        self.target_color_index = random.randint(0, len(self.COLORS) - 1)
        target_name, target_rgb = self.COLORS[self.target_color_index]

        # Show target color on display
        self.display.clear()
        self.display.show_text(f"Round {self.level}", x=35, y=0)
        self.display.show_text(f"Find: {target_name}", x=25, y=25)
        self.display.show_text("Get ready...", x=25, y=50)

        # Brief pause to show target
        time.sleep(1.5)

        # Countdown
        for i in range(self.COUNTDOWN_TIME, 0, -1):
            self.display.clear()
            self.display.show_centered_text(str(i), y=20, scale=3)
            self.sound.play_countdown()
            time.sleep(1.0)

        # Generate random colors for all keys
        self._generate_key_colors()

        # Display colors on keys
        self._render_keys()

        # Show game display
        self._update_display()

        self.round_start_time = time.monotonic()
        self.in_round = True
        print(f"[DEBUG] {self.NAME} round {self.level} started, target={target_name}, matches={len(self.matching_keys)}")

    def _generate_key_colors(self):
        """Assign random colors to all keys, ensuring some match target."""
        self.key_colors = []
        self.matching_keys = set()

        # Ensure at least 2-4 keys match the target
        num_matches = random.randint(2, 4)
        match_positions = set()
        while len(match_positions) < num_matches:
            match_positions.add(random.randint(0, 11))

        for i in range(12):
            if i in match_positions:
                self.key_colors.append(self.target_color_index)
                self.matching_keys.add(i)
            else:
                # Pick a random non-target color
                other_colors = [c for c in range(len(self.COLORS)) if c != self.target_color_index]
                self.key_colors.append(random.choice(other_colors))

    def _render_keys(self):
        """Display colors on all keys."""
        for i in range(12):
            if i in self.found_keys:
                # Already found - show dim version or off
                self.leds.set_key(i, (30, 30, 30))
            else:
                color_idx = self.key_colors[i]
                _, rgb = self.COLORS[color_idx]
                self.leds.set_key(i, rgb)

    def _update_display(self):
        """Update the OLED display."""
        target_name, _ = self.COLORS[self.target_color_index]

        # Calculate times
        game_elapsed = time.monotonic() - self.game_start_time
        game_remaining = max(0, self.GAME_DURATION - game_elapsed)
        round_elapsed = time.monotonic() - self.round_start_time if self.round_start_time else 0
        round_remaining = max(0, self.round_time - round_elapsed)

        self.display.clear()
        self.display.show_text(f"Find: {target_name}", x=0, y=0)
        self.display.show_text(f"Score: {self.score}", x=0, y=15)
        self.display.show_text(f"Round: {int(round_remaining)}s", x=0, y=35)
        self.display.show_text(f"Game: {int(game_remaining)}s", x=0, y=50)

        remaining = len(self.matching_keys) - len(self.found_keys)
        self.display.show_text(f"Left: {remaining}", x=80, y=15)

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        current_time = time.monotonic()

        # Check overall game time
        game_elapsed = current_time - self.game_start_time
        if game_elapsed >= self.GAME_DURATION:
            print(f"[DEBUG] {self.NAME} game time expired")
            self._handle_game_over()
            return False

        if self.in_round:
            # Check round time
            round_elapsed = current_time - self.round_start_time
            if round_elapsed >= self.round_time:
                print(f"[DEBUG] {self.NAME} round time expired")
                # Round failed - still continue but no bonus
                self.sound.play_wrong()
                self.leds.flash_all('red', times=2, on_time=0.1, off_time=0.1)
                time.sleep(0.5)
                self._start_new_round()
                return True

            # Update display periodically
            self._update_display()

        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed and self.in_round:
            self.handle_key_press(key_event.key_number)

        # Check for pause
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            if not self.handle_pause():
                return False
            # Resume - restart current round
            self._start_new_round()

        return self.is_running

    def handle_key_press(self, key_index):
        """Handle key press."""
        if key_index in self.found_keys:
            # Already pressed this one
            return

        if key_index in self.matching_keys:
            self._handle_correct(key_index)
        else:
            self._handle_wrong(key_index)

    def _handle_correct(self, key_index):
        """Handle correct key press."""
        self.found_keys.add(key_index)
        self.correct_hits += 1
        self.score += self.POINTS_PER_CORRECT

        # Visual/audio feedback
        self.leds.set_key(key_index, (30, 30, 30))  # Dim to show found
        self.sound.play_tone(660, 0.05)

        # Check if all matches found
        if self.found_keys == self.matching_keys:
            self._handle_round_complete()

    def _handle_wrong(self, key_index):
        """Handle wrong key press."""
        self.wrong_hits += 1
        self.score = max(0, self.score + self.POINTS_PER_WRONG)

        # Flash red briefly
        self.leds.flash_key(key_index, 'red', times=1, on_time=0.1, off_time=0)
        self.sound.play_tone(220, 0.1)

        # Re-render to restore color
        self._render_keys()

    def _handle_round_complete(self):
        """Handle successful round completion."""
        print(f"[DEBUG] {self.NAME} round {self.level} complete!")

        # Bonus points for completing round
        self.score += 20

        # Success animation
        self.sound.play_correct()
        self.leds.flash_all('green', times=2, on_time=0.1, off_time=0.1)

        # Increase speed for next round
        self.round_time = max(self.MIN_ROUND_TIME, self.round_time - self.ROUND_TIME_DECREASE)

        time.sleep(0.3)
        self._start_new_round()

    def _handle_game_over(self):
        """Handle game over."""
        print(f"[DEBUG] {self.NAME}._handle_game_over()")
        self.is_running = False
        self.game_over = True

        self.update_high_score()

        self.leds.clear_all()
        self.sound.play_level_up()
        self.leds.sweep_animation('green')

        self.display.clear()
        self.display.show_centered_text("TIME'S UP!", y=5, scale=2)
        self.display.show_centered_text(f"Score: {self.score}", y=30)
        self.display.show_centered_text(f"Rounds: {self.level}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)

        self.wait_for_continue()
        print(f"[DEBUG] {self.NAME}._handle_game_over() complete")

    def reset(self):
        """Reset game state."""
        self.target_color_index = 0
        self.key_colors = []
        self.matching_keys = set()
        self.found_keys = set()
        self.round_time = self.INITIAL_ROUND_TIME
        self.round_start_time = None
        self.game_start_time = None
        self.level = 0
        self.score = 0
        self.correct_hits = 0
        self.wrong_hits = 0
        self.in_round = False
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
