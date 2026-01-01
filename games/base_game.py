"""
Base game class for MacroPad games.

All games inherit from this class to ensure consistent interface and behavior.
"""


class BaseGame:
    """Abstract base class for all MacroPad games."""

    # Class attributes (override in subclasses)
    NAME = "Base Game"
    DESCRIPTION = "Base game description"

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """
        Initialize the game.

        Args:
            macropad: Adafruit MacroPad object
            sound_manager: SoundManager instance
            led_manager: LEDManager instance
            display_manager: DisplayManager instance
        """
        self.macropad = macropad
        self.sound = sound_manager
        self.leds = led_manager
        self.display = display_manager
        self.score = 0
        self.high_score = 0
        self.is_running = False
        self.game_over = False

    def start(self):
        """
        Initialize and start the game.
        Called when game is selected from menu.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement start()")

    def update(self):
        """
        Main game loop tick. Called repeatedly while game is running.

        Returns:
            bool: True if game should continue, False if game over or exit requested
        """
        raise NotImplementedError("Subclasses must implement update()")

    def handle_key_press(self, key_index):
        """
        Handle a key press event.

        Args:
            key_index: Integer 0-11 indicating which key was pressed
        """
        raise NotImplementedError("Subclasses must implement handle_key_press()")

    def handle_encoder_change(self, delta):
        """
        Handle rotary encoder rotation (optional, for in-game use).

        Args:
            delta: Integer indicating rotation direction (+1 or -1)
        """
        # Optional - default implementation does nothing
        pass

    def handle_encoder_press(self):
        """
        Handle encoder button press (typically pause/menu).
        Default implementation returns False to exit game.
        """
        return False

    def reset(self):
        """
        Reset game state for a new round.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement reset()")

    def cleanup(self):
        """Clean up resources when exiting game."""
        print(f"[DEBUG] {self.NAME}.cleanup() called")
        self.leds.clear_all()
        self.display.clear()
        self.is_running = False
        self.game_over = False
        print(f"[DEBUG] {self.NAME}.cleanup() complete")

    def update_high_score(self):
        """Update high score if current score is higher."""
        if self.score > self.high_score:
            self.high_score = self.score
            return True
        return False

    def show_game_over_screen(self, reason=None):
        """
        Display standard game over screen and wait for encoder press.

        Args:
            reason: Optional reason string (e.g., "Time's up!")
        """
        print(f"[DEBUG] {self.NAME}.show_game_over_screen(reason={reason})")
        self.update_high_score()
        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        if reason:
            self.display.show_centered_text(reason, y=28)
        self.display.show_centered_text(f"Score: {self.score}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
        print(f"[DEBUG] {self.NAME} calling wait_for_continue()")
        self.wait_for_continue()
        print(f"[DEBUG] {self.NAME} wait_for_continue() returned")

    def wait_for_continue(self):
        """Wait for encoder button press to continue."""
        import time

        print("[DEBUG] wait_for_continue() - waiting for encoder press")
        # Clear any pending button state
        self.macropad.encoder_switch_debounced.update()

        while True:
            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                print("[DEBUG] wait_for_continue() - encoder pressed, returning")
                return
            time.sleep(0.05)

    def do_countdown(self, seconds=3):
        """
        Display a countdown before game starts.

        Args:
            seconds: Number of seconds to count down
        """
        import time
        for i in range(seconds, 0, -1):
            self.display.show_countdown(i)
            self.sound.play_countdown()
            self.leds.flash_all('white', times=1, on_time=0.3, off_time=0.7)
        self.display.clear()
        self.display.show_centered_text("GO!", y=20, scale=2)
        self.sound.play_menu_select()
        time.sleep(0.5)

    def handle_pause(self):
        """
        Handle pause request. Shows pause menu and waits for input.

        Returns:
            bool: True to continue game, False to quit to menu
        """
        import time

        print(f"[DEBUG] {self.NAME}.handle_pause() called")
        self.display.show_pause_menu()
        self.leds.clear_all()

        while True:
            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                print(f"[DEBUG] {self.NAME}.handle_pause() - encoder pressed, returning False (quit)")
                return False  # Quit to menu

            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                print(f"[DEBUG] {self.NAME}.handle_pause() - key pressed, returning True (resume)")
                return True  # Resume game

            time.sleep(0.05)
