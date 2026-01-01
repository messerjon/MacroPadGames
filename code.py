"""
MacroPad RP2040 Game Collection

Main entry point for a collection of six mini-games.
Use the rotary encoder to scroll through games and press to select.

Games included:
1. Speed Chase - Press the lit key before time runs out
2. Simon Says - Repeat the sequence
3. Whack-a-Mole - Hit the moles before they hide
4. Color Match - Find the matching color
5. Memory Grid - Remember the pattern
6. Lights Out - Turn off all the lights

Hardware: Adafruit MacroPad RP2040
- 12 mechanical keys with NeoPixel LEDs
- 128x64 OLED display
- Rotary encoder with push button
- Piezo speaker
"""

import time
import json
from adafruit_macropad import MacroPad

# Import utility managers
from utils.sound_manager import SoundManager
from utils.led_manager import LEDManager
from utils.display_manager import DisplayManager

# Import games
from games.speed_chase import SpeedChase
from games.simon_says import SimonSays
from games.whack_a_mole import WhackAMole
from games.color_match import ColorMatch
from games.memory_grid import MemoryGrid
from games.lights_out import LightsOut
from games.reaction_timer import ReactionTimer
from games.piano import Piano
from games.pattern_copy import PatternCopy
from games.hot_potato import HotPotato
from games.tictactoe import TicTacToe


# Game registry
GAMES = [
    ("Speed Chase", SpeedChase),
    ("Simon Says", SimonSays),
    ("Whack-a-Mole", WhackAMole),
    ("Color Match", ColorMatch),
    ("Memory Grid", MemoryGrid),
    ("Lights Out", LightsOut),
    ("Reaction", ReactionTimer),
    ("Piano", Piano),
    ("Pattern Copy", PatternCopy),
    ("Hot Potato", HotPotato),
    ("Tic-Tac-Toe", TicTacToe),
]


class MenuSystem:
    """Main menu system for game selection and management."""

    SCORES_FILE = "/scores.json"

    def __init__(self, macropad):
        """
        Initialize the menu system.

        Args:
            macropad: Adafruit MacroPad object
        """
        self.macropad = macropad
        self.sound_manager = SoundManager(macropad)
        self.led_manager = LEDManager(macropad)
        self.display_manager = DisplayManager(macropad)

        self.current_selection = 0
        self.last_encoder_position = macropad.encoder
        self.current_game = None
        self._menu_needs_redraw = True  # Track when menu needs updating

        # Load high scores from file (or initialize empty)
        self.high_scores = self._load_scores()
        print(f"[DEBUG] Loaded high scores: {self.high_scores}")

    def _load_scores(self):
        """Load high scores from file."""
        default_scores = {name: 0 for name, _ in GAMES}
        try:
            with open(self.SCORES_FILE, "r") as f:
                saved_scores = json.load(f)
                # Merge with defaults (in case new games were added)
                for name in default_scores:
                    if name in saved_scores:
                        default_scores[name] = saved_scores[name]
                return default_scores
        except (OSError, ValueError) as e:
            print(f"[DEBUG] Could not load scores: {e}")
            return default_scores

    def _save_scores(self):
        """Save high scores to file."""
        try:
            with open(self.SCORES_FILE, "w") as f:
                json.dump(self.high_scores, f)
            print(f"[DEBUG] Saved high scores: {self.high_scores}")
            return True
        except OSError as e:
            # Filesystem may be read-only (USB connected)
            print(f"[DEBUG] Could not save scores: {e}")
            return False

    def run(self):
        """Main loop - handles menu and game state transitions."""
        print("[DEBUG] MenuSystem.run() starting")
        # Show startup animation
        self._show_startup()
        print("[DEBUG] Startup complete, entering main loop")

        while True:
            if self.current_game is None:
                if self._menu_needs_redraw:
                    print("[DEBUG] Menu needs redraw, showing menu")
                    self._show_menu()
                    self._menu_needs_redraw = False
                self._handle_menu_input()
            else:
                try:
                    game_name = GAMES[self.current_selection][0]
                    result = self.current_game.update()
                    if not result:
                        # Game ended - save high score and cleanup
                        print(f"[DEBUG] Game '{game_name}' update() returned False, ending game")
                        print(f"[DEBUG] Game state: is_running={self.current_game.is_running}, game_over={self.current_game.game_over}")
                        if self.current_game.high_score > self.high_scores[game_name]:
                            self.high_scores[game_name] = self.current_game.high_score
                            print(f"[DEBUG] New high score: {self.high_scores[game_name]}")
                            self._save_scores()  # Persist to file
                        print("[DEBUG] Calling cleanup()")
                        self.current_game.cleanup()
                        self.current_game = None
                        self._menu_needs_redraw = True
                        print("[DEBUG] Returning to menu")
                except Exception as e:
                    # Handle unexpected errors gracefully
                    import traceback
                    print(f"[ERROR] Game error: {e}")
                    traceback.print_exception(type(e), e, e.__traceback__)
                    self.current_game = None
                    self._menu_needs_redraw = True
                    self.led_manager.clear_all()
                    self.display_manager.clear()
                    self.display_manager.show_centered_text("Error!", y=20)
                    time.sleep(2.0)

    def _show_startup(self):
        """Display startup animation."""
        self.display_manager.clear()
        self.display_manager.show_centered_text("MacroPad", y=10, scale=2)
        self.display_manager.show_centered_text("Games", y=35, scale=2)

        # LED sweep animation
        self.led_manager.rainbow_cycle(duration=1.5)
        self.led_manager.clear_all()

        self.sound_manager.play_menu_select()
        time.sleep(0.5)

    def _show_menu(self):
        """Display game selection menu on OLED."""
        self.display_manager.clear()

        # Title
        self.display_manager.show_text("SELECT GAME", x=20, y=0)

        # Calculate visible items (limited display space)
        max_visible = 4
        num_games = len(GAMES)
        start_idx = max(0, min(self.current_selection - 1, num_games - max_visible))

        for i in range(min(max_visible, num_games)):
            item_idx = start_idx + i
            if item_idx < num_games:
                game_name = GAMES[item_idx][0]
                prefix = ">" if item_idx == self.current_selection else " "
                y_pos = 14 + i * 12
                self.display_manager.show_text(f"{prefix}{game_name}", x=0, y=y_pos)

        # Show high score for selected game
        selected_name = GAMES[self.current_selection][0]
        high_score = self.high_scores.get(selected_name, 0)
        if high_score > 0:
            self.display_manager.show_text(f"Best:{high_score}", x=0, y=52)

        # Show volume indicator vertically on far right
        vol = self.sound_manager.volume
        vol_char = "V" if vol > 0 else "M"
        self.display_manager.show_text(vol_char, x=122, y=0)
        # Show volume bars vertically (top to bottom = high to low)
        for i in range(5):
            bar = "#" if (5 - i) <= vol else "-"
            self.display_manager.show_text(bar, x=122, y=12 + i * 10)

        # Update LEDs for menu
        self._menu_led_animation()

    def _menu_led_animation(self):
        """Display LED indicators for menu."""
        self.led_manager.clear_all()

        # Show volume control keys (right column)
        # Key 2 = volume up (dim if at max, else green)
        if self.sound_manager.volume < 5:
            self.led_manager.set_key(2, (0, 255, 0))    # Green
        else:
            self.led_manager.set_key(2, (0, 50, 0))     # Dim green

        # Key 5 = volume down (dim if at min, else orange)
        if self.sound_manager.volume > 0:
            self.led_manager.set_key(5, (255, 100, 0))  # Orange
        else:
            self.led_manager.set_key(5, (50, 20, 0))    # Dim orange

    def _handle_menu_input(self):
        """Process encoder rotation and button press in menu."""
        # Check encoder rotation
        current_encoder = self.macropad.encoder
        encoder_delta = current_encoder - self.last_encoder_position

        if encoder_delta != 0:
            self.last_encoder_position = current_encoder
            self.current_selection = (self.current_selection + encoder_delta) % len(GAMES)
            print(f"[DEBUG] Menu: encoder rotated, selection={self.current_selection}")
            self.sound_manager.play_tone(440, 0.02)  # Quick feedback
            self._menu_needs_redraw = True

        # Check encoder button press
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            print(f"[DEBUG] Menu: encoder pressed, starting game {self.current_selection}")
            self._start_game()

        # Check for key presses (volume control only)
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            key = key_event.key_number
            print(f"[DEBUG] Menu: key {key} pressed")

            # Volume up (key 2)
            if key == 2:
                if self.sound_manager.volume_up():
                    print(f"[DEBUG] Menu: volume up to {self.sound_manager.volume}")
                    self._menu_needs_redraw = True
                    self.sound_manager.play_tone(550, 0.02)

            # Volume down (key 5)
            elif key == 5:
                if self.sound_manager.volume_down():
                    print(f"[DEBUG] Menu: volume down to {self.sound_manager.volume}")
                    self._menu_needs_redraw = True
                    # Play feedback tone if not muted
                    if self.sound_manager.enabled:
                        self.sound_manager.play_tone(330, 0.02)

        # Small delay to prevent tight loop
        time.sleep(0.05)

    def _start_game(self):
        """Instantiate and start the selected game."""
        game_name, game_class = GAMES[self.current_selection]
        print(f"[DEBUG] _start_game() called for '{game_name}'")

        self.sound_manager.play_menu_select()
        self.led_manager.clear_all()

        # Create game instance
        print(f"[DEBUG] Creating game instance: {game_class.__name__}")
        self.current_game = game_class(
            self.macropad,
            self.sound_manager,
            self.led_manager,
            self.display_manager
        )

        # Restore high score from session
        self.current_game.high_score = self.high_scores.get(game_name, 0)
        print(f"[DEBUG] Restored high score: {self.current_game.high_score}")

        # Start the game
        try:
            print(f"[DEBUG] Calling {game_class.__name__}.start()")
            self.current_game.start()
            print(f"[DEBUG] Game started, is_running={self.current_game.is_running}")
        except Exception as e:
            import traceback
            print(f"[ERROR] Failed to start game: {e}")
            traceback.print_exception(type(e), e, e.__traceback__)
            self.current_game = None
            self._menu_needs_redraw = True
            self.display_manager.clear()
            self.display_manager.show_centered_text("Start Error", y=20)
            time.sleep(2.0)


def main():
    """Main entry point."""
    # Initialize MacroPad
    macropad = MacroPad()

    # Create and run menu system
    menu = MenuSystem(macropad)

    try:
        menu.run()
    except KeyboardInterrupt:
        # Clean exit
        macropad.pixels.fill((0, 0, 0))
        macropad.display.root_group = None


# Run the application
if __name__ == "__main__":
    main()
else:
    # When imported as code.py on CircuitPython, run directly
    main()
