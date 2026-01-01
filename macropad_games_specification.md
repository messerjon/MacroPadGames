# MacroPad RP2040 Game Collection Specification

## Project Overview

A collection of six mini-games for the Adafruit MacroPad RP2040, selectable via the rotary encoder. The MacroPad features 12 mechanical keys with individual NeoPixel RGB LEDs, a rotary encoder with push button, a 128x64 OLED display, and a speaker.

### Hardware Reference

| Component | Specification |
|-----------|---------------|
| Keys | 12 mechanical switches (3 columns × 4 rows) |
| LEDs | 12 NeoPixels (one per key), addressable RGB |
| Display | 128×64 monochrome OLED (SH1106 or SSD1306) |
| Audio | Piezo speaker on pin A0 |
| Encoder | Rotary encoder with integrated push button |
| MCU | RP2040 (Dual ARM Cortex-M0+) |

### Key Layout Reference

```
┌─────┬─────┬─────┐
│  0  │  1  │  2  │
├─────┼─────┼─────┤
│  3  │  4  │  5  │
├─────┼─────┼─────┤
│  6  │  7  │  8  │
├─────┼─────┼─────┤
│  9  │ 10  │ 11  │
└─────┴─────┴─────┘
```

Keys are indexed 0-11, left-to-right, top-to-bottom.

---

## System Architecture

### File Structure

```
CIRCUITPY/
├── code.py                 # Main entry point
├── lib/
│   ├── adafruit_macropad.mpy
│   ├── adafruit_display_text/
│   ├── adafruit_displayio_sh1106.mpy
│   └── neopixel.mpy
├── games/
│   ├── __init__.py
│   ├── base_game.py        # Abstract base class for all games
│   ├── speed_chase.py      # Game 1: Speed Chase
│   ├── simon_says.py       # Game 2: Simon Says
│   ├── whack_a_mole.py     # Game 3: Whack-a-Mole
│   ├── color_match.py      # Game 4: Color Match
│   ├── memory_grid.py      # Game 5: Memory Grid
│   └── lights_out.py       # Game 6: Lights Out
├── sounds/
│   ├── menu_music.wav      # Menu background music (optional)
│   ├── correct.wav         # Correct button press
│   ├── wrong.wav           # Wrong button press / game over
│   ├── level_up.wav        # Level advancement
│   └── game_start.wav      # Game starting
└── utils/
    ├── __init__.py
    ├── sound_manager.py    # Audio playback utilities
    ├── led_manager.py      # NeoPixel animation utilities
    └── display_manager.py  # OLED text/graphics utilities
```

### Base Game Class

All games inherit from a common base class to ensure consistent interface and behavior.

```python
# games/base_game.py

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
        """Initialize and start the game. Called when game is selected."""
        raise NotImplementedError
    
    def update(self):
        """
        Main game loop tick. Called repeatedly while game is running.
        
        Returns:
            bool: True if game should continue, False if game over or exit requested
        """
        raise NotImplementedError
    
    def handle_key_press(self, key_index):
        """
        Handle a key press event.
        
        Args:
            key_index: Integer 0-11 indicating which key was pressed
        """
        raise NotImplementedError
    
    def handle_encoder_change(self, delta):
        """
        Handle rotary encoder rotation (optional, for in-game use).
        
        Args:
            delta: Integer indicating rotation direction (+1 or -1)
        """
        pass
    
    def handle_encoder_press(self):
        """Handle encoder button press (typically pause/menu)."""
        pass
    
    def reset(self):
        """Reset game state for a new round."""
        raise NotImplementedError
    
    def cleanup(self):
        """Clean up resources when exiting game."""
        self.leds.clear_all()
        self.display.clear()
```

### Main Menu System

```python
# code.py - Main entry point

"""
Main menu system for MacroPad Game Collection.

Rotary encoder scrolls through game list.
Encoder button press selects/starts the highlighted game.
During gameplay, encoder button returns to menu (after confirmation).
"""

GAMES = [
    ("Speed Chase", SpeedChase),
    ("Simon Says", SimonSays),
    ("Whack-a-Mole", WhackAMole),
    ("Color Match", ColorMatch),
    ("Memory Grid", MemoryGrid),
    ("Lights Out", LightsOut),
]

class MenuSystem:
    def __init__(self, macropad):
        self.macropad = macropad
        self.current_selection = 0
        self.last_encoder_position = macropad.encoder
        self.current_game = None
        
    def run(self):
        """Main loop - handles menu and game state transitions."""
        while True:
            if self.current_game is None:
                self.show_menu()
                self.handle_menu_input()
            else:
                if not self.current_game.update():
                    self.current_game.cleanup()
                    self.current_game = None
    
    def show_menu(self):
        """Display game selection menu on OLED."""
        # Show game list with current selection highlighted
        # Show high scores if available
        # Animate LEDs in idle pattern
        pass
    
    def handle_menu_input(self):
        """Process encoder rotation and button press in menu."""
        # Encoder rotation: change selection
        # Encoder press: start selected game
        pass
    
    def start_game(self, game_class):
        """Instantiate and start the selected game."""
        self.current_game = game_class(
            self.macropad,
            self.sound_manager,
            self.led_manager,
            self.display_manager
        )
        self.current_game.start()
```

---

## Utility Modules

### Sound Manager

```python
# utils/sound_manager.py

"""
Sound management for MacroPad games.

Handles both WAV file playback and tone generation.
WAV files should be 16-bit mono at 22050 Hz for best compatibility.
"""

class SoundManager:
    # Predefined tones for synthesized sounds
    TONES = {
        'correct': [(880, 0.1), (1100, 0.1)],      # A5 -> C#6 ascending
        'wrong': [(440, 0.2), (220, 0.3)],         # A4 -> A3 descending
        'level_up': [(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.2)],  # C5-E5-G5-C6
        'game_over': [(440, 0.2), (349, 0.2), (294, 0.2), (220, 0.4)],  # Descending
        'menu_select': [(660, 0.05), (880, 0.05)], # Quick chirp
        'countdown': [(440, 0.1)],                  # Single beep
        'key_feedback': {                           # Different tone per key
            0: 262,   # C4
            1: 294,   # D4
            2: 330,   # E4
            3: 349,   # F4
            4: 392,   # G4
            5: 440,   # A4
            6: 494,   # B4
            7: 523,   # C5
            8: 587,   # D5
            9: 659,   # E5
            10: 698,  # F5
            11: 784,  # G5
        }
    }
    
    def __init__(self, macropad):
        self.macropad = macropad
        self.enabled = True
    
    def play_tone(self, frequency, duration):
        """Play a single tone."""
        if self.enabled:
            self.macropad.play_tone(frequency, duration)
    
    def play_sequence(self, tone_sequence):
        """Play a sequence of (frequency, duration) tuples."""
        if self.enabled:
            for freq, dur in tone_sequence:
                self.macropad.play_tone(freq, dur)
    
    def play_correct(self):
        """Play correct answer sound."""
        self.play_sequence(self.TONES['correct'])
    
    def play_wrong(self):
        """Play wrong answer / game over sound."""
        self.play_sequence(self.TONES['wrong'])
    
    def play_key_tone(self, key_index):
        """Play the tone associated with a specific key."""
        freq = self.TONES['key_feedback'].get(key_index, 440)
        self.play_tone(freq, 0.15)
    
    def play_wav(self, filename):
        """Play a WAV file (if available)."""
        # Implementation depends on audioio availability
        pass
    
    def toggle(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
```

### LED Manager

```python
# utils/led_manager.py

"""
NeoPixel LED management for MacroPad games.

Provides color constants, animations, and utility functions.
"""

class LEDManager:
    # Color constants (RGB tuples, 0-255)
    COLORS = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 128, 0),
        'purple': (128, 0, 255),
        'pink': (255, 105, 180),
        'white': (255, 255, 255),
        'off': (0, 0, 0),
    }
    
    # Game-specific color sets
    GAME_COLORS = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
    
    def __init__(self, macropad):
        self.macropad = macropad
        self.pixels = macropad.pixels
        self.brightness = 0.5
        self.pixels.brightness = self.brightness
    
    def set_key(self, key_index, color):
        """
        Set a single key's LED color.
        
        Args:
            key_index: Integer 0-11
            color: RGB tuple or color name string
        """
        if isinstance(color, str):
            color = self.COLORS.get(color, self.COLORS['off'])
        self.pixels[key_index] = color
    
    def set_all(self, color):
        """Set all keys to the same color."""
        if isinstance(color, str):
            color = self.COLORS.get(color, self.COLORS['off'])
        self.pixels.fill(color)
    
    def clear_all(self):
        """Turn off all LEDs."""
        self.pixels.fill(self.COLORS['off'])
    
    def get_random_color(self):
        """Return a random color from GAME_COLORS."""
        import random
        color_name = random.choice(self.GAME_COLORS)
        return self.COLORS[color_name], color_name
    
    def flash_key(self, key_index, color, times=3, on_time=0.1, off_time=0.1):
        """Flash a single key."""
        import time
        for _ in range(times):
            self.set_key(key_index, color)
            time.sleep(on_time)
            self.set_key(key_index, 'off')
            time.sleep(off_time)
    
    def flash_all(self, color, times=3, on_time=0.1, off_time=0.1):
        """Flash all keys simultaneously."""
        import time
        for _ in range(times):
            self.set_all(color)
            time.sleep(on_time)
            self.clear_all()
            time.sleep(off_time)
    
    def sweep_animation(self, color, delay=0.05):
        """Sweep color across all keys left-to-right, top-to-bottom."""
        import time
        for i in range(12):
            self.set_key(i, color)
            time.sleep(delay)
        for i in range(12):
            self.set_key(i, 'off')
            time.sleep(delay)
    
    def rainbow_cycle(self, duration=2.0):
        """Display a rainbow animation across all keys."""
        import time
        start = time.monotonic()
        while time.monotonic() - start < duration:
            # Implement rainbow wheel animation
            pass
    
    def dim_key(self, key_index, factor=0.5):
        """Dim a key's current color by a factor."""
        current = self.pixels[key_index]
        dimmed = tuple(int(c * factor) for c in current)
        self.pixels[key_index] = dimmed
```

### Display Manager

```python
# utils/display_manager.py

"""
OLED display management for MacroPad games.

Handles text rendering, score display, and simple graphics.
"""

class DisplayManager:
    def __init__(self, macropad):
        self.macropad = macropad
        self.display = macropad.display
        self.display_group = displayio.Group()
        self.display.root_group = self.display_group
    
    def clear(self):
        """Clear the display."""
        while len(self.display_group):
            self.display_group.pop()
    
    def show_text(self, text, x=0, y=0, scale=1):
        """Display text at specified position."""
        # Use adafruit_display_text
        pass
    
    def show_centered_text(self, text, y=None, scale=1):
        """Display text centered horizontally."""
        pass
    
    def show_title(self, title):
        """Display a game title (large, centered at top)."""
        self.show_centered_text(title, y=5, scale=2)
    
    def show_score(self, score, label="Score"):
        """Display current score."""
        self.show_text(f"{label}: {score}", x=0, y=50)
    
    def show_game_over(self, score, high_score=None):
        """Display game over screen."""
        self.clear()
        self.show_centered_text("GAME OVER", y=10, scale=2)
        self.show_centered_text(f"Score: {score}", y=35)
        if high_score:
            self.show_centered_text(f"Best: {high_score}", y=50)
    
    def show_countdown(self, number):
        """Display a countdown number (large, centered)."""
        self.clear()
        self.show_centered_text(str(number), y=20, scale=3)
    
    def show_level(self, level):
        """Display current level."""
        self.show_text(f"Level: {level}", x=80, y=0)
    
    def show_instructions(self, lines):
        """Display multiple lines of instruction text."""
        self.clear()
        for i, line in enumerate(lines):
            self.show_text(line, x=0, y=i * 12)
```

---

## Game 1: Speed Chase

### Concept
A single random key lights up. The player must press it before time runs out. Each successful press causes the next key to light up faster. The game ends when the player presses the wrong key or runs out of time.

### Game States

```
┌──────────────┐
│    START     │
│  (Countdown) │
└──────┬───────┘
       │
       ▼
┌──────────────┐    Wrong Key    ┌──────────────┐
│   PLAYING    │ ──────────────► │  GAME OVER   │
│ (Show target)│                 │ (Show score) │
└──────┬───────┘                 └──────┬───────┘
       │                                │
       │ Correct Key                    │ Encoder Press
       ▼                                ▼
┌──────────────┐                 ┌──────────────┐
│   FEEDBACK   │                 │    MENU      │
│ (Brief flash)│                 └──────────────┘
└──────┬───────┘
       │
       │ (Faster timing)
       ▼
┌──────────────┐
│ NEXT ROUND   │
│ (New target) │
└──────────────┘
```

### Detailed Specification

```python
# games/speed_chase.py

class SpeedChase(BaseGame):
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
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.current_target = None
        self.target_color = None
        self.time_limit = self.INITIAL_TIME_LIMIT
        self.target_start_time = None
        self.round_number = 0
    
    def start(self):
        """Initialize game state and show countdown."""
        self.reset()
        self.display.show_title(self.NAME)
        self.sound.play_sequence(self.sound.TONES['countdown'])
        
        # 3-2-1 countdown with display and LED animation
        for i in range(3, 0, -1):
            self.display.show_countdown(i)
            self.leds.flash_all('white', times=1, on_time=0.3, off_time=0.7)
        
        self.display.show_centered_text("GO!", y=20, scale=2)
        self.sound.play_wav('game_start.wav')  # Or play_sequence
        time.sleep(0.5)
        
        self.is_running = True
        self._show_next_target()
    
    def _show_next_target(self):
        """Select and display a new random target key."""
        import random
        
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
        self.display.show_score(self.score)
        self.display.show_text(f"Round: {self.round_number}", x=0, y=0)
        # Show time remaining as progress bar (optional)
    
    def update(self):
        """Main game loop - check for timeout."""
        if not self.is_running:
            return False
        
        # Check for timeout
        elapsed = time.monotonic() - self.target_start_time
        if elapsed >= self.time_limit:
            self._handle_timeout()
            return False
        
        # Check for key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            self.handle_key_press(key_event.key_number)
        
        # Check for encoder press (pause/quit)
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            return self._handle_pause()
        
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
        
        # Brief visual feedback - flash the key
        self.leds.flash_key(self.current_target, 'green', times=2, on_time=0.05, off_time=0.05)
        
        # Decrease time limit for next round (increase difficulty)
        self.time_limit = max(self.MINIMUM_TIME_LIMIT, self.time_limit * self.TIME_DECREASE_FACTOR)
        
        # Show next target
        self._show_next_target()
    
    def _handle_wrong_press(self, pressed_key):
        """Handle wrong key press - game over."""
        self.is_running = False
        self.game_over = True
        
        # Visual feedback - flash wrong key red, correct key green
        self.leds.set_key(pressed_key, 'red')
        self.leds.set_key(self.current_target, 'green')
        self.sound.play_wrong()
        time.sleep(1.0)
        
        # Flash all red for game over
        self.leds.flash_all('red', times=3, on_time=0.2, off_time=0.2)
        
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Show game over screen
        self.display.show_game_over(self.score, self.high_score)
    
    def _handle_timeout(self):
        """Handle timeout - game over."""
        self.is_running = False
        self.game_over = True
        
        # Visual feedback - flash target key indicating missed
        self.leds.flash_key(self.current_target, 'red', times=5, on_time=0.1, off_time=0.1)
        self.sound.play_wrong()
        
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Show game over screen
        self.display.show_game_over(self.score, self.high_score)
        self.display.show_text("Time's up!", x=0, y=40)
    
    def _handle_pause(self):
        """Handle pause/quit request."""
        # Show pause menu, return False to exit or True to continue
        self.display.clear()
        self.display.show_centered_text("PAUSED", y=10)
        self.display.show_text("Press to quit", x=10, y=35)
        self.display.show_text("Any key: resume", x=5, y=50)
        
        while True:
            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                return False  # Quit to menu
            
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                # Resume game
                self._show_next_target()  # Re-show current target
                return True
    
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
```

---

## Game 2: Simon Says

### Concept
Classic memory game. The game plays an increasingly long sequence of colors/keys. The player must repeat the sequence exactly. Each successful round adds one more step to the sequence.

### Game States

```
┌──────────────┐
│    START     │
│ (Show intro) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ SHOW SEQUENCE│ ◄─────────────┐
│ (Play colors)│               │
└──────┬───────┘               │
       │                       │
       ▼                       │
┌──────────────┐    Correct    │
│ PLAYER INPUT │ ──────────────┘
│ (Wait keys)  │    (Add step)
└──────┬───────┘
       │ Wrong
       ▼
┌──────────────┐
│  GAME OVER   │
│ (Show score) │
└──────────────┘
```

### Detailed Specification

```python
# games/simon_says.py

class SimonSays(BaseGame):
    NAME = "Simon Says"
    DESCRIPTION = "Repeat the sequence!"
    
    # Configuration
    SEQUENCE_DISPLAY_TIME = 0.5   # Time each key is shown
    SEQUENCE_GAP_TIME = 0.2       # Gap between sequence items
    INPUT_TIMEOUT = 5.0           # Time allowed per input
    SPEED_INCREASE_INTERVAL = 5   # Speed up every N levels
    MIN_DISPLAY_TIME = 0.2        # Fastest display time
    
    # The four Simon colors (using 4 specific keys)
    # Using keys in a 2x2 pattern in the center-ish area
    SIMON_KEYS = [3, 4, 7, 8]     # Middle 2x2 grid
    SIMON_COLORS = {
        3: ('red', (255, 0, 0)),
        4: ('blue', (0, 0, 255)),
        7: ('green', (0, 255, 0)),
        8: ('yellow', (255, 255, 0)),
    }
    
    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.sequence = []
        self.player_position = 0
        self.current_display_time = self.SEQUENCE_DISPLAY_TIME
        self.waiting_for_input = False
        self.input_start_time = None
    
    def start(self):
        """Initialize game."""
        self.reset()
        
        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(1.0)
        
        # Highlight the four Simon keys
        for key in self.SIMON_KEYS:
            color_name, color_rgb = self.SIMON_COLORS[key]
            self.leds.set_key(key, color_rgb)
        time.sleep(1.5)
        self.leds.clear_all()
        
        self.is_running = True
        self._add_to_sequence()
        self._play_sequence()
    
    def _add_to_sequence(self):
        """Add a random step to the sequence."""
        import random
        new_key = random.choice(self.SIMON_KEYS)
        self.sequence.append(new_key)
    
    def _play_sequence(self):
        """Display the current sequence to the player."""
        self.waiting_for_input = False
        
        # Show level
        level = len(self.sequence)
        self.display.clear()
        self.display.show_text(f"Level: {level}", x=0, y=0)
        self.display.show_text("Watch...", x=0, y=30)
        
        time.sleep(0.5)
        
        # Play each item in sequence
        for key in self.sequence:
            color_name, color_rgb = self.SIMON_COLORS[key]
            
            # Light up key and play tone
            self.leds.set_key(key, color_rgb)
            self.sound.play_key_tone(key)
            time.sleep(self.current_display_time)
            
            # Turn off
            self.leds.set_key(key, 'off')
            time.sleep(self.SEQUENCE_GAP_TIME)
        
        # Ready for player input
        self.player_position = 0
        self.waiting_for_input = True
        self.input_start_time = time.monotonic()
        
        # Show dim colors on Simon keys as hints
        for key in self.SIMON_KEYS:
            color_name, color_rgb = self.SIMON_COLORS[key]
            dim_color = tuple(c // 4 for c in color_rgb)
            self.leds.set_key(key, dim_color)
        
        self.display.clear()
        self.display.show_text(f"Level: {level}", x=0, y=0)
        self.display.show_text("Your turn!", x=0, y=30)
    
    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False
        
        if self.waiting_for_input:
            # Check for timeout
            if time.monotonic() - self.input_start_time > self.INPUT_TIMEOUT:
                self._handle_game_over("Time's up!")
                return False
            
            # Check for key presses
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self.handle_key_press(key_event.key_number)
        
        # Check for encoder press (pause)
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            return self._handle_pause()
        
        return self.is_running
    
    def handle_key_press(self, key_index):
        """Process player input."""
        if not self.waiting_for_input:
            return
        
        # Only accept Simon keys
        if key_index not in self.SIMON_KEYS:
            # Flash to indicate invalid key, but don't penalize
            self.leds.flash_key(key_index, 'white', times=1)
            return
        
        expected_key = self.sequence[self.player_position]
        
        if key_index == expected_key:
            self._handle_correct_input(key_index)
        else:
            self._handle_wrong_input(key_index, expected_key)
    
    def _handle_correct_input(self, key_index):
        """Handle correct key press."""
        # Visual/audio feedback
        color_name, color_rgb = self.SIMON_COLORS[key_index]
        self.leds.set_key(key_index, color_rgb)
        self.sound.play_key_tone(key_index)
        time.sleep(0.2)
        
        # Dim back
        dim_color = tuple(c // 4 for c in color_rgb)
        self.leds.set_key(key_index, dim_color)
        
        self.player_position += 1
        self.input_start_time = time.monotonic()  # Reset timeout
        
        # Check if sequence complete
        if self.player_position >= len(self.sequence):
            self._handle_level_complete()
    
    def _handle_wrong_input(self, pressed_key, expected_key):
        """Handle wrong key press."""
        # Show what was pressed (red) vs what was expected (green)
        self.leds.clear_all()
        self.leds.set_key(pressed_key, 'red')
        self.leds.set_key(expected_key, 'green')
        self.sound.play_wrong()
        time.sleep(1.5)
        
        self._handle_game_over("Wrong key!")
    
    def _handle_level_complete(self):
        """Handle successful completion of a level."""
        self.score = len(self.sequence)
        
        # Celebration animation
        self.leds.clear_all()
        self.sound.play_sequence(self.sound.TONES['level_up'])
        self.leds.flash_all('green', times=2, on_time=0.1, off_time=0.1)
        
        # Speed up every N levels
        if self.score % self.SPEED_INCREASE_INTERVAL == 0:
            self.current_display_time = max(
                self.MIN_DISPLAY_TIME,
                self.current_display_time * 0.85
            )
        
        # Add next step and continue
        time.sleep(0.5)
        self._add_to_sequence()
        self._play_sequence()
    
    def _handle_game_over(self, reason):
        """Handle game over."""
        self.is_running = False
        self.game_over = True
        
        if self.score > self.high_score:
            self.high_score = self.score
        
        self.leds.flash_all('red', times=3)
        
        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        self.display.show_centered_text(reason, y=25)
        self.display.show_centered_text(f"Level: {self.score}", y=40)
        self.display.show_centered_text(f"Best: {self.high_score}", y=52)
    
    def _handle_pause(self):
        """Handle pause."""
        # Similar to SpeedChase pause
        pass
    
    def reset(self):
        """Reset for new game."""
        self.sequence = []
        self.player_position = 0
        self.current_display_time = self.SEQUENCE_DISPLAY_TIME
        self.waiting_for_input = False
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
```

---

## Game 3: Whack-a-Mole

### Concept
Multiple "moles" (lit keys) appear simultaneously and disappear after a short time. The player scores points by pressing lit keys before they disappear. Difficulty increases with more simultaneous moles and shorter visibility times.

### Game States

```
┌──────────────┐
│    START     │
│ (Countdown)  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│              PLAYING                  │
│  ┌─────────────┐    ┌─────────────┐  │
│  │ Spawn Timer │───►│ Spawn Moles │  │
│  └─────────────┘    └──────┬──────┘  │
│                            │         │
│  ┌─────────────┐    ┌──────▼──────┐  │
│  │ Despawn     │◄───│ Mole Active │  │
│  │ (Timeout)   │    │ (Wait hit)  │  │
│  └─────────────┘    └─────────────┘  │
└───────────────┬──────────────────────┘
                │ Game timer expires
                ▼
         ┌──────────────┐
         │  GAME OVER   │
         │ (Show score) │
         └──────────────┘
```

### Detailed Specification

```python
# games/whack_a_mole.py

class WhackAMole(BaseGame):
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
        
        # Countdown
        self.display.show_title(self.NAME)
        for i in range(3, 0, -1):
            self.display.show_countdown(i)
            self.leds.flash_all('white', times=1)
            time.sleep(1.0)
        
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
        
        # Update display
        self._update_display()
        
        # Check for pause
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            return self._handle_pause()
        
        return True
    
    def _spawn_mole(self):
        """Spawn a new mole on a random unoccupied key."""
        import random
        
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
            # Hit!
            self._handle_hit(key_index)
        else:
            # Miss!
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
        
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Clear remaining moles
        self.leds.clear_all()
        
        # Victory animation
        self.sound.play_sequence(self.sound.TONES['level_up'])
        self.leds.sweep_animation('green')
        
        # Show results
        self.display.clear()
        self.display.show_centered_text("TIME'S UP!", y=5, scale=2)
        self.display.show_centered_text(f"Score: {self.score}", y=30)
        self.display.show_centered_text(f"Hits: {self.hits} Miss: {self.misses}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
    
    def _handle_pause(self):
        """Handle pause - returns whether to continue."""
        # Implementation similar to other games
        pass
    
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
```

---

## Game 4: Color Match

### Concept
All keys display cycling colors. One "target" key flashes to indicate the color to find. The player must press any OTHER key that currently shows the same color. Colors cycle continuously, requiring quick reactions.

### Game States

```
┌──────────────┐
│    START     │
│ (Show rules) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ SHOW TARGET  │ ◄─────────────┐
│ (Flash key)  │               │
└──────┬───────┘               │
       │                       │
       ▼                       │
┌──────────────┐    Correct    │
│   PLAYING    │ ──────────────┘
│(Colors cycle)│
└──────┬───────┘
       │ Wrong / Timeout
       ▼
┌──────────────┐
│  GAME OVER   │
└──────────────┘
```

### Detailed Specification

```python
# games/color_match.py

class ColorMatch(BaseGame):
    NAME = "Color Match"
    DESCRIPTION = "Find the matching color!"
    
    # Configuration
    INITIAL_CYCLE_SPEED = 0.8     # Seconds per color change
    MIN_CYCLE_SPEED = 0.2         # Fastest cycle speed
    CYCLE_SPEED_DECREASE = 0.05   # Speed increase per level
    TARGET_FLASH_TIME = 0.5       # How long target flashes
    INPUT_TIMEOUT = 5.0           # Time to find match
    
    # Colors used in the game
    MATCH_COLORS = [
        ('red', (255, 0, 0)),
        ('green', (0, 255, 0)),
        ('blue', (0, 0, 255)),
        ('yellow', (255, 255, 0)),
        ('cyan', (0, 255, 255)),
        ('magenta', (255, 0, 255)),
    ]
    
    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.key_colors = [0] * 12        # Index into MATCH_COLORS for each key
        self.key_offsets = []             # Random offset for each key's cycle
        self.target_key = None
        self.target_color_index = None
        self.cycle_speed = self.INITIAL_CYCLE_SPEED
        self.last_cycle_time = None
        self.round_start_time = None
        self.level = 0
    
    def start(self):
        """Initialize game."""
        self.reset()
        
        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.show_text("Match the flashing", x=5, y=30)
        self.display.show_text("key's color!", x=25, y=42)
        time.sleep(2.0)
        
        # Initialize random color offsets for each key
        import random
        self.key_offsets = [random.randint(0, len(self.MATCH_COLORS) - 1) for _ in range(12)]
        
        self.is_running = True
        self.last_cycle_time = time.monotonic()
        self._start_new_round()
    
    def _start_new_round(self):
        """Start a new matching round."""
        import random
        
        self.level += 1
        
        # Select random target key and capture its current color
        self.target_key = random.randint(0, 11)
        self.target_color_index = self.key_colors[self.target_key]
        
        # Flash the target key to show the color to match
        target_color_name, target_color_rgb = self.MATCH_COLORS[self.target_color_index]
        
        self.display.clear()
        self.display.show_text(f"Level: {self.level}", x=0, y=0)
        self.display.show_text(f"Find: {target_color_name.upper()}", x=0, y=30)
        
        # Flash target
        for _ in range(3):
            self.leds.set_key(self.target_key, 'white')
            time.sleep(0.1)
            self.leds.set_key(self.target_key, target_color_rgb)
            time.sleep(0.2)
        
        self.round_start_time = time.monotonic()
    
    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False
        
        current_time = time.monotonic()
        
        # Check for timeout
        if current_time - self.round_start_time > self.INPUT_TIMEOUT:
            self._handle_game_over("Time's up!")
            return False
        
        # Update color cycle
        if current_time - self.last_cycle_time >= self.cycle_speed:
            self._cycle_colors()
            self.last_cycle_time = current_time
        
        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            self.handle_key_press(key_event.key_number)
        
        # Check for pause
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            return self._handle_pause()
        
        return self.is_running
    
    def _cycle_colors(self):
        """Advance all keys to their next color."""
        for i in range(12):
            if i == self.target_key:
                # Target key stays on target color (highlighted)
                color_name, color_rgb = self.MATCH_COLORS[self.target_color_index]
                # Make it pulse/brighter to stand out
                self.leds.set_key(i, color_rgb)
            else:
                # Other keys cycle through colors with their offset
                self.key_colors[i] = (self.key_colors[i] + 1) % len(self.MATCH_COLORS)
                actual_index = (self.key_colors[i] + self.key_offsets[i]) % len(self.MATCH_COLORS)
                color_name, color_rgb = self.MATCH_COLORS[actual_index]
                self.leds.set_key(i, color_rgb)
    
    def handle_key_press(self, key_index):
        """Handle key press."""
        if key_index == self.target_key:
            # Can't press the target key itself
            self.leds.flash_key(key_index, 'white', times=1)
            return
        
        # Check if pressed key's current color matches target
        actual_index = (self.key_colors[key_index] + self.key_offsets[key_index]) % len(self.MATCH_COLORS)
        
        if actual_index == self.target_color_index:
            self._handle_correct(key_index)
        else:
            self._handle_wrong(key_index)
    
    def _handle_correct(self, key_index):
        """Handle correct color match."""
        self.score += 10
        
        # Feedback
        self.sound.play_correct()
        self.leds.flash_key(key_index, 'white', times=2, on_time=0.1, off_time=0.1)
        
        # Increase difficulty
        self.cycle_speed = max(self.MIN_CYCLE_SPEED, self.cycle_speed - self.CYCLE_SPEED_DECREASE)
        
        # Next round
        time.sleep(0.3)
        self._start_new_round()
    
    def _handle_wrong(self, key_index):
        """Handle wrong color selection."""
        self.sound.play_wrong()
        
        # Show what colors were
        pressed_index = (self.key_colors[key_index] + self.key_offsets[key_index]) % len(self.MATCH_COLORS)
        pressed_name, _ = self.MATCH_COLORS[pressed_index]
        target_name, _ = self.MATCH_COLORS[self.target_color_index]
        
        self._handle_game_over(f"Wrong! {pressed_name} != {target_name}")
    
    def _handle_game_over(self, reason):
        """Handle game over."""
        self.is_running = False
        self.game_over = True
        
        if self.score > self.high_score:
            self.high_score = self.score
        
        self.leds.flash_all('red', times=3)
        
        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        self.display.show_centered_text(reason, y=28)
        self.display.show_centered_text(f"Score: {self.score}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
    
    def _handle_pause(self):
        """Handle pause."""
        pass
    
    def reset(self):
        """Reset game state."""
        self.key_colors = [0] * 12
        self.key_offsets = []
        self.target_key = None
        self.target_color_index = None
        self.cycle_speed = self.INITIAL_CYCLE_SPEED
        self.score = 0
        self.level = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
```

---

## Game 5: Memory Grid

### Concept
A pattern of keys lights up briefly, then all lights turn off. The player must press ALL the keys that were lit (in any order). Unlike Simon Says, the order doesn't matter—just remembering which keys were part of the pattern.

### Game States

```
┌──────────────┐
│    START     │
│  (Intro)     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ SHOW PATTERN │ ◄─────────────┐
│ (Display N   │               │
│  keys lit)   │               │
└──────┬───────┘               │
       │                       │
       │ (Goes dark)           │
       ▼                       │
┌──────────────┐    All Found  │
│ PLAYER INPUT │ ──────────────┘
│ (Find all    │   (Add 1 key)
│  lit keys)   │
└──────┬───────┘
       │ Wrong key
       ▼
┌──────────────┐
│  GAME OVER   │
└──────────────┘
```

### Detailed Specification

```python
# games/memory_grid.py

class MemoryGrid(BaseGame):
    NAME = "Memory Grid"
    DESCRIPTION = "Remember the pattern!"
    
    # Configuration
    INITIAL_PATTERN_SIZE = 3      # Start with 3 keys lit
    MAX_PATTERN_SIZE = 10         # Maximum keys in pattern
    DISPLAY_TIME_BASE = 1.5       # Base time to show pattern
    DISPLAY_TIME_PER_KEY = 0.3    # Additional time per key
    INPUT_TIMEOUT = 10.0          # Time to complete input
    
    # Colors
    PATTERN_COLOR = (0, 150, 255) # Cyan-blue for pattern
    CORRECT_COLOR = (0, 255, 0)   # Green for correct
    WRONG_COLOR = (255, 0, 0)     # Red for wrong
    HINT_COLOR = (30, 30, 30)     # Dim for unfound keys (optional hint mode)
    
    def __init__(self, macropad, sound_manager, led_manager, display_manager):
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
        import random
        
        self.level += 1
        self.found = set()
        
        # Generate random pattern
        all_keys = list(range(12))
        random.shuffle(all_keys)
        self.pattern = set(all_keys[:self.pattern_size])
        
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
            return self._handle_pause()
        
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
        self.sound.play_sequence(self.sound.TONES['level_up'])
        self.leds.flash_all('green', times=2)
        
        # Increase difficulty
        if self.pattern_size < self.MAX_PATTERN_SIZE:
            self.pattern_size += 1
        
        time.sleep(0.5)
        self._start_new_round()
    
    def _handle_game_over(self, reason):
        """Handle game over."""
        self.is_running = False
        self.game_over = True
        
        if self.score > self.high_score:
            self.high_score = self.score
        
        self.leds.flash_all('red', times=3)
        
        self.display.clear()
        self.display.show_centered_text("GAME OVER", y=5, scale=2)
        self.display.show_centered_text(reason, y=28)
        self.display.show_centered_text(f"Level: {self.level}", y=42)
        self.display.show_centered_text(f"Best: {self.high_score}", y=54)
    
    def _handle_pause(self):
        """Handle pause."""
        pass
    
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
```

---

## Game 6: Lights Out

### Concept
Classic puzzle game. All keys start lit (or in a random pattern). Pressing a key toggles that key AND its adjacent neighbors (up, down, left, right). The goal is to turn all lights OFF.

### Key Adjacency Map

```
Key Layout:
┌─────┬─────┬─────┐
│  0  │  1  │  2  │
├─────┼─────┼─────┤
│  3  │  4  │  5  │
├─────┼─────┼─────┤
│  6  │  7  │  8  │
├─────┼─────┼─────┤
│  9  │ 10  │ 11  │
└─────┴─────┴─────┘

Adjacency (including self):
0: [0, 1, 3]
1: [0, 1, 2, 4]
2: [1, 2, 5]
3: [0, 3, 4, 6]
4: [1, 3, 4, 5, 7]
5: [2, 4, 5, 8]
6: [3, 6, 7, 9]
7: [4, 6, 7, 8, 10]
8: [5, 7, 8, 11]
9: [6, 9, 10]
10: [7, 9, 10, 11]
11: [8, 10, 11]
```

### Game States

```
┌──────────────┐
│    START     │
│(Setup puzzle)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   PLAYING    │
│ (Toggle keys)│ ◄───┐
└──────┬───────┘     │
       │             │
       │ Key press   │
       ▼             │
┌──────────────┐     │
│   TOGGLE     │─────┘
│ (Flip keys)  │
└──────┬───────┘
       │ All off?
       ▼
┌──────────────┐
│   VICTORY    │
│ (Show moves) │
└──────────────┘
```

### Detailed Specification

```python
# games/lights_out.py

class LightsOut(BaseGame):
    NAME = "Lights Out"
    DESCRIPTION = "Turn off all the lights!"
    
    # Adjacency map for 3x4 grid
    ADJACENCY = {
        0: [0, 1, 3],
        1: [0, 1, 2, 4],
        2: [1, 2, 5],
        3: [0, 3, 4, 6],
        4: [1, 3, 4, 5, 7],
        5: [2, 4, 5, 8],
        6: [3, 6, 7, 9],
        7: [4, 6, 7, 8, 10],
        8: [5, 7, 8, 11],
        9: [6, 9, 10],
        10: [7, 9, 10, 11],
        11: [8, 10, 11],
    }
    
    # Configuration
    INITIAL_RANDOM_MOVES = 5      # Random moves to scramble starting position
    MAX_RANDOM_MOVES = 15         # Maximum scramble for harder levels
    
    # Colors
    LIGHT_ON = (255, 200, 50)     # Warm yellow for "on"
    LIGHT_OFF = (0, 0, 0)         # Off
    TOGGLE_FLASH = (255, 255, 255) # White flash when toggling
    
    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.lights = [False] * 12  # True = on, False = off
        self.move_count = 0
        self.level = 1
        self.random_moves = self.INITIAL_RANDOM_MOVES
    
    def start(self):
        """Start the game."""
        self.reset()
        
        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.show_text("Press a key to", x=10, y=25)
        self.display.show_text("toggle it + neighbors", x=0, y=37)
        self.display.show_text("Goal: All lights off!", x=0, y=52)
        time.sleep(3.0)
        
        self.is_running = True
        self._generate_puzzle()
    
    def _generate_puzzle(self):
        """Generate a solvable puzzle by working backwards."""
        import random
        
        # Start with all lights off
        self.lights = [False] * 12
        
        # Apply random moves to create puzzle
        # This guarantees the puzzle is solvable
        for _ in range(self.random_moves):
            key = random.randint(0, 11)
            self._toggle_lights(key, animate=False)
        
        # Make sure at least some lights are on
        while sum(self.lights) == 0:
            key = random.randint(0, 11)
            self._toggle_lights(key, animate=False)
        
        self.move_count = 0
        self._update_display()
        self._render_lights()
    
    def _toggle_lights(self, key_index, animate=True):
        """Toggle the pressed key and its neighbors."""
        affected_keys = self.ADJACENCY[key_index]
        
        if animate:
            # Flash affected keys
            for key in affected_keys:
                self.leds.set_key(key, self.TOGGLE_FLASH)
            self.sound.play_tone(440, 0.05)
            time.sleep(0.05)
        
        # Toggle each affected key
        for key in affected_keys:
            self.lights[key] = not self.lights[key]
        
        if animate:
            self._render_lights()
    
    def _render_lights(self):
        """Update LED display based on current light state."""
        for i in range(12):
            if self.lights[i]:
                self.leds.set_key(i, self.LIGHT_ON)
            else:
                self.leds.set_key(i, self.LIGHT_OFF)
    
    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False
        
        # Handle key presses
        key_event = self.macropad.keys.events.get()
        if key_event and key_event.pressed:
            self.handle_key_press(key_event.key_number)
        
        # Check for encoder actions
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            return self._handle_pause()
        
        # Encoder rotation could reset puzzle or give hint
        encoder_delta = self.macropad.encoder - getattr(self, '_last_encoder', self.macropad.encoder)
        if encoder_delta != 0:
            self._last_encoder = self.macropad.encoder
            # Could implement hint or undo functionality
        
        return self.is_running
    
    def handle_key_press(self, key_index):
        """Handle key press - toggle lights."""
        self._toggle_lights(key_index)
        self.move_count += 1
        self._update_display()
        
        # Check for win condition
        if not any(self.lights):
            self._handle_victory()
    
    def _update_display(self):
        """Update OLED display."""
        self.display.clear()
        self.display.show_text(f"Level: {self.level}", x=0, y=0)
        self.display.show_text(f"Moves: {self.move_count}", x=0, y=50)
        
        lights_on = sum(self.lights)
        self.display.show_text(f"Lights: {lights_on}/12", x=60, y=0)
    
    def _handle_victory(self):
        """Handle puzzle solved."""
        self.is_running = False
        
        # Calculate score (fewer moves = higher score)
        base_score = 100
        move_penalty = self.move_count * 2
        level_bonus = self.level * 20
        self.score = max(10, base_score - move_penalty + level_bonus)
        
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Victory animation
        self.sound.play_sequence(self.sound.TONES['level_up'])
        self.leds.sweep_animation('green')
        
        # Show results
        self.display.clear()
        self.display.show_centered_text("SOLVED!", y=5, scale=2)
        self.display.show_centered_text(f"Moves: {self.move_count}", y=30)
        self.display.show_centered_text(f"Score: {self.score}", y=42)
        
        time.sleep(2.0)
        
        # Prompt for next level or menu
        self.display.show_text("Press key: Next", x=5, y=52)
        self.display.show_text("Encoder: Menu", x=5, y=62)
        
        # Wait for input
        while True:
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self._next_level()
                return
            
            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                self.game_over = True
                return
    
    def _next_level(self):
        """Advance to next level."""
        self.level += 1
        self.random_moves = min(self.MAX_RANDOM_MOVES, self.random_moves + 1)
        self.is_running = True
        self._generate_puzzle()
    
    def _handle_pause(self):
        """Handle pause - show options."""
        self.display.clear()
        self.display.show_centered_text("PAUSED", y=10)
        self.display.show_text("Encoder: Quit", x=20, y=30)
        self.display.show_text("Any key: Resume", x=15, y=42)
        
        while True:
            self.macropad.encoder_switch_debounced.update()
            if self.macropad.encoder_switch_debounced.pressed:
                return False  # Quit
            
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self._update_display()
                self._render_lights()
                return True  # Resume
    
    def reset(self):
        """Reset game state."""
        self.lights = [False] * 12
        self.move_count = 0
        self.level = 1
        self.random_moves = self.INITIAL_RANDOM_MOVES
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
```

---

## Sound Design

### Tone Specifications

All tones use the MacroPad's built-in `play_tone(frequency, duration)` function.

| Sound | Notes | Frequencies (Hz) | Durations (s) |
|-------|-------|------------------|---------------|
| Correct | Ascending | 880, 1100 | 0.1, 0.1 |
| Wrong | Descending | 440, 220 | 0.2, 0.3 |
| Level Up | C-E-G-C arpeggio | 523, 659, 784, 1047 | 0.1, 0.1, 0.1, 0.2 |
| Game Over | Descending | 440, 349, 294, 220 | 0.2, 0.2, 0.2, 0.4 |
| Menu Select | Quick chirp | 660, 880 | 0.05, 0.05 |
| Countdown | Single beep | 440 | 0.1 |
| Key 0-11 | Musical scale | C4-G5 | 0.15 each |

### Optional WAV Files

For richer audio (if storage permits):

| File | Description | Format |
|------|-------------|--------|
| menu_music.wav | Idle menu loop | 22050 Hz, 16-bit mono |
| game_start.wav | Game starting fanfare | 22050 Hz, 16-bit mono |
| victory.wav | Level/game complete | 22050 Hz, 16-bit mono |

---

## Implementation Notes

### CircuitPython Version
- Target: CircuitPython 8.x or 9.x
- Required libraries from Adafruit Bundle:
  - `adafruit_macropad`
  - `adafruit_display_text`
  - `adafruit_displayio_sh1106` or `adafruit_displayio_ssd1306`
  - `neopixel`

### Memory Considerations
- RP2040 has limited RAM (~260KB)
- Use `mpy` compiled files where possible
- Avoid large data structures
- Clear event queues regularly
- Consider lazy loading games

### Timing
- Use `time.monotonic()` for all timing (not `time.time()`)
- Non-blocking design where possible
- Keep main loop responsive (< 50ms per iteration)

### Display Refresh
- Don't refresh display every loop iteration
- Update only when state changes
- Use display groups efficiently

### Error Handling
- Wrap file operations in try/except
- Gracefully handle missing WAV files
- Reset to menu on unhandled exceptions

---

## Testing Checklist

### Per-Game Tests
- [ ] Game starts correctly from menu
- [ ] All keys respond properly
- [ ] Scoring works correctly
- [ ] High score persists during session
- [ ] Game over triggers correctly
- [ ] Pause/resume works
- [ ] Return to menu works
- [ ] Visual feedback is clear
- [ ] Audio feedback plays

### System Tests
- [ ] Menu navigation with encoder
- [ ] Game selection with encoder press
- [ ] Transitions between games
- [ ] Long play session stability
- [ ] Memory usage remains stable
- [ ] No LED flickering
- [ ] Display remains readable

---

## Future Enhancements

### Potential Additions
1. **High Score Persistence**: Save to `settings.toml` or JSON file
2. **Difficulty Settings**: Easy/Medium/Hard via encoder in menu
3. **Sound Toggle**: Mute option accessible from menu
4. **Brightness Control**: Adjust LED brightness via settings
5. **Statistics**: Track games played, total time, etc.
6. **Combo Mode**: Play through all games in sequence
7. **Two-Player Games**: Alternating turns on same device

### Additional Games to Consider
- Piano/Music Mode (not a game, but fun)
- Reaction Time Test
- Pattern Creator (design then play)
- Snake (using all 12 keys as mini display)
