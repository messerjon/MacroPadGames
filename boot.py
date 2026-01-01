"""
Boot configuration for MacroPad Games.

Controls filesystem write access:
- Hold KEY 0 during boot: USB drive is writable (for updating code)
- Normal boot: CircuitPython can write (for saving high scores)

To update code on the device:
1. Hold the top-left key (key 0) while plugging in USB
2. The CIRCUITPY drive will be writable from your computer
3. Copy your updated files
4. Unplug and replug normally to play with score saving enabled
"""

import board
import digitalio
import storage
import usb_cdc

# Set up key 0 (top-left) as input with pull-up
key = digitalio.DigitalInOut(board.KEY1)  # KEY1 is physical key 0
key.direction = digitalio.Direction.INPUT
key.pull = digitalio.Pull.UP

# Key pressed = LOW (pull-up, so pressed connects to ground)
key_pressed = not key.value

if key_pressed:
    # Key held during boot - USB has write access (normal mode for editing)
    # CircuitPython is read-only
    print("Boot: USB write mode (key held)")
else:
    # Normal boot - CircuitPython has write access for saving scores
    # USB drive is read-only to computer
    storage.remount("/", readonly=False)
    print("Boot: Game mode (scores will save)")

key.deinit()
