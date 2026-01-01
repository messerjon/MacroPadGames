"""
Piano Mode for MacroPad.

Turn your MacroPad into a musical instrument!
Each key plays a different note. Use encoder to change octave.
Not really a game - more of a toy/instrument mode.
"""

import time
from .base_game import BaseGame


class Piano(BaseGame):
    """Piano - Play music on your MacroPad!"""

    NAME = "Piano"
    DESCRIPTION = "Play music!"

    # Note frequencies for chromatic scale (C4 to B4, then C5 to B5)
    # Layout matches piano: bottom row is lower notes
    # Key layout:
    #  0   1   2      C4  C#4  D4
    #  3   4   5      D#4 E4   F4
    #  6   7   8      F#4 G4   G#4
    #  9  10  11      A4  A#4  B4

    BASE_NOTES = {
        0: 262,   # C4
        1: 277,   # C#4
        2: 294,   # D4
        3: 311,   # D#4
        4: 330,   # E4
        5: 349,   # F4
        6: 370,   # F#4
        7: 392,   # G4
        8: 415,   # G#4
        9: 440,   # A4
        10: 466,  # A#4
        11: 494,  # B4
    }

    NOTE_NAMES = {
        0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F",
        6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B"
    }

    # Colors for notes (rainbow pattern)
    NOTE_COLORS = {
        0: (255, 0, 0),      # C - Red
        1: (255, 64, 0),     # C# - Red-Orange
        2: (255, 128, 0),    # D - Orange
        3: (255, 200, 0),    # D# - Yellow-Orange
        4: (255, 255, 0),    # E - Yellow
        5: (128, 255, 0),    # F - Yellow-Green
        6: (0, 255, 0),      # F# - Green
        7: (0, 255, 128),    # G - Green-Cyan
        8: (0, 255, 255),    # G# - Cyan
        9: (0, 128, 255),    # A - Cyan-Blue
        10: (0, 0, 255),     # A# - Blue
        11: (128, 0, 255),   # B - Purple
    }

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Piano mode."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.octave = 4  # Starting octave (C4)
        self.octave_multiplier = 1.0
        self.keys_pressed = set()
        self._last_encoder = 0

    def start(self):
        """Initialize piano mode."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.clear()
        self.display.show_text("Play the keys!", x=20, y=15)
        self.display.show_text("Encoder: octave", x=15, y=30)
        self.display.show_text("Press enc to exit", x=5, y=45)
        time.sleep(2.0)

        self._last_encoder = self.macropad.encoder
        self.is_running = True
        self._update_display()
        self._show_keyboard()
        print(f"[DEBUG] {self.NAME}.start() complete")

    def _show_keyboard(self):
        """Show dim colors on all keys."""
        for key in range(12):
            r, g, b = self.NOTE_COLORS[key]
            # Dim version
            self.leds.set_key(key, (r // 4, g // 4, b // 4))

    def _update_display(self):
        """Update the display."""
        self.display.clear()
        self.display.show_text("PIANO MODE", x=25, y=0)
        self.display.show_text(f"Octave: {self.octave}", x=35, y=25)
        self.display.show_text("Encoder to exit", x=15, y=52)

    def update(self):
        """Main loop."""
        if not self.is_running:
            return False

        # Check for octave change via encoder
        current_encoder = self.macropad.encoder
        encoder_delta = current_encoder - self._last_encoder
        if encoder_delta != 0:
            self._last_encoder = current_encoder
            self.octave = max(2, min(7, self.octave + encoder_delta))
            self.octave_multiplier = 2 ** (self.octave - 4)
            self._update_display()
            self.sound.play_tone(262 * self.octave_multiplier, 0.05)

        # Check for exit
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            self.is_running = False
            return False

        # Handle key events
        key_event = self.macropad.keys.events.get()
        if key_event:
            if key_event.pressed:
                self._key_pressed(key_event.key_number)
            else:
                self._key_released(key_event.key_number)

        return True

    def _key_pressed(self, key_index):
        """Handle key press - play note."""
        self.keys_pressed.add(key_index)

        # Get frequency for this key
        base_freq = self.BASE_NOTES[key_index]
        freq = int(base_freq * self.octave_multiplier)

        # Light up key
        self.leds.set_key(key_index, self.NOTE_COLORS[key_index])

        # Play tone
        self.sound.play_tone(freq, 0.15)

        # Show note name
        note_name = self.NOTE_NAMES[key_index]
        self.display.clear()
        self.display.show_centered_text(f"{note_name}{self.octave}", y=15, scale=2)
        self.display.show_text(f"Octave: {self.octave}", x=35, y=45)

    def _key_released(self, key_index):
        """Handle key release."""
        self.keys_pressed.discard(key_index)

        # Dim the key
        r, g, b = self.NOTE_COLORS[key_index]
        self.leds.set_key(key_index, (r // 4, g // 4, b // 4))

        # If no keys pressed, restore display
        if not self.keys_pressed:
            self._update_display()

    def handle_key_press(self, key_index):
        """Handle key press - delegated to update loop."""
        pass

    def reset(self):
        """Reset state."""
        self.octave = 4
        self.octave_multiplier = 1.0
        self.keys_pressed = set()
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
