# MacroPad Games

A collection of 11 mini-games for the **Adafruit MacroPad RP2040**.

Turn your macro keyboard into a portable game console!

## Games

| Game | Description |
|------|-------------|
| **Speed Chase** | Press the lit key before time runs out. Gets faster each round! |
| **Simon Says** | Classic memory game. Repeat the sequence of colors. |
| **Whack-a-Mole** | Hit the moles before they hide. 30 seconds of chaos! |
| **Color Match** | Find all keys matching the target color before time expires. |
| **Memory Grid** | Remember which keys lit up, then find them all. |
| **Lights Out** | Toggle puzzle - turn off all the lights! |
| **Reaction** | Test your reflexes. Wait for green, then press FAST! |
| **Piano** | Play music on your MacroPad. Encoder changes octave. |
| **Pattern Copy** | Memorize a pattern, then copy it exactly. |
| **Hot Potato** | Pass it quick! Don't hold it when it explodes! |
| **Tic-Tac-Toe** | 2-player classic on the bottom 9 keys. |

## Hardware Requirements

- [Adafruit MacroPad RP2040](https://www.adafruit.com/product/5128)
- CircuitPython 8.x or later

## Installation

1. Install CircuitPython on your MacroPad
2. Copy the required libraries to `CIRCUITPY/lib/`:
   - `adafruit_macropad.mpy`
   - `adafruit_display_text/`
   - `neopixel.mpy`
   - `adafruit_hid/`
   - `adafruit_midi/`
   - `adafruit_debouncer.mpy`
   - `adafruit_ticks.mpy`
3. Copy all files from this repo to `CIRCUITPY/`

## Controls

### Menu
- **Rotary Encoder**: Scroll through games
- **Encoder Press**: Select game
- **Key 2** (top-right): Volume up
- **Key 5**: Volume down

### In-Game
- **Keys**: Game-specific controls
- **Encoder Press**: Pause / Exit to menu

## High Scores

High scores are saved automatically and persist between power cycles!

### Boot Modes

| Mode | How to Enter | Description |
|------|--------------|-------------|
| **Game Mode** | Normal boot | Scores save, USB drive read-only |
| **Edit Mode** | Hold **key 0** while plugging in | USB drive writable for updates |

To update code: Hold top-left key while connecting USB, copy files, then replug normally.

## Project Structure

```
MacroPadGames/
├── code.py              # Main entry point
├── boot.py              # Boot configuration for score saving
├── games/
│   ├── base_game.py     # Base class for all games
│   ├── speed_chase.py
│   ├── simon_says.py
│   ├── whack_a_mole.py
│   ├── color_match.py
│   ├── memory_grid.py
│   ├── lights_out.py
│   ├── reaction_timer.py
│   ├── piano.py
│   ├── pattern_copy.py
│   ├── hot_potato.py
│   └── tictactoe.py
└── utils/
    ├── sound_manager.py
    ├── led_manager.py
    └── display_manager.py
```

## Adding New Games

1. Create a new file in `games/` that inherits from `BaseGame`
2. Implement required methods: `start()`, `update()`, `handle_key_press()`, `reset()`
3. Add import to `games/__init__.py`
4. Add to `GAMES` list in `code.py`

## License

MIT License - Feel free to modify and share!

## Credits

Built with [Claude Code](https://claude.ai/claude-code)
