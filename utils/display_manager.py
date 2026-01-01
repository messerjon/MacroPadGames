"""
OLED display management for MacroPad games.

Handles text rendering, score display, and simple graphics.
Display is 128x64 monochrome OLED.
"""

import displayio
from adafruit_display_text import label
import terminalio


class DisplayManager:
    """Manages the OLED display on the MacroPad."""

    # Display dimensions
    WIDTH = 128
    HEIGHT = 64

    # Character dimensions (approximate for terminalio.FONT)
    CHAR_WIDTH = 6
    CHAR_HEIGHT = 12

    def __init__(self, macropad):
        """
        Initialize the display manager.

        Args:
            macropad: Adafruit MacroPad object
        """
        self.macropad = macropad
        self.display = macropad.display
        self.display_group = displayio.Group()
        self.display.root_group = self.display_group
        self._labels = []

    def clear(self):
        """Clear the display by removing all elements."""
        # Remove all elements from group
        while len(self.display_group):
            self.display_group.pop()
        self._labels = []

        # Create fresh group to ensure clean state
        self.display_group = displayio.Group()
        self.display.root_group = self.display_group

    def show_text(self, text, x=0, y=0, scale=1, color=0xFFFFFF):
        """
        Display text at specified position.

        Args:
            text: Text string to display
            x: X position (pixels from left)
            y: Y position (pixels from top)
            scale: Text scale factor
            color: Text color (hex)
        """
        text_label = label.Label(
            terminalio.FONT,
            text=text,
            color=color,
            scale=scale,
            x=x,
            y=y + (self.CHAR_HEIGHT * scale // 2)  # Adjust for vertical centering
        )
        self.display_group.append(text_label)
        self._labels.append(text_label)
        return text_label

    def show_centered_text(self, text, y=None, scale=1, color=0xFFFFFF):
        """
        Display text centered horizontally.

        Args:
            text: Text string to display
            y: Y position (pixels from top). If None, centers vertically too.
            scale: Text scale factor
            color: Text color (hex)
        """
        text_width = len(text) * self.CHAR_WIDTH * scale
        x = (self.WIDTH - text_width) // 2

        if y is None:
            y = (self.HEIGHT - self.CHAR_HEIGHT * scale) // 2

        return self.show_text(text, x=x, y=y, scale=scale, color=color)

    def show_title(self, title):
        """
        Display a game title (large, centered at top).

        Args:
            title: Title string
        """
        self.show_centered_text(title, y=5, scale=2)

    def show_score(self, score, label_text="Score"):
        """
        Display current score at bottom of screen.

        Args:
            score: Score value
            label_text: Label prefix
        """
        self.show_text(f"{label_text}: {score}", x=0, y=50)

    def show_game_over(self, score, high_score=None):
        """
        Display game over screen.

        Args:
            score: Final score
            high_score: Best score (optional)
        """
        self.clear()
        self.show_centered_text("GAME OVER", y=10, scale=2)
        self.show_centered_text(f"Score: {score}", y=35)
        if high_score is not None:
            self.show_centered_text(f"Best: {high_score}", y=50)

    def show_countdown(self, number):
        """
        Display a countdown number (large, centered).

        Args:
            number: Number to display
        """
        self.clear()
        self.show_centered_text(str(number), y=20, scale=3)

    def show_level(self, level, x=80, y=0):
        """
        Display current level.

        Args:
            level: Level number
            x: X position
            y: Y position
        """
        self.show_text(f"Level: {level}", x=x, y=y)

    def show_instructions(self, lines):
        """
        Display multiple lines of instruction text.

        Args:
            lines: List of text strings
        """
        self.clear()
        for i, line in enumerate(lines):
            self.show_text(line, x=0, y=i * 12)

    def show_menu(self, items, selected_index, title="Select Game"):
        """
        Display a menu with selectable items.

        Args:
            items: List of menu item strings
            selected_index: Currently selected item index
            title: Menu title
        """
        self.clear()

        # Show title
        self.show_text(title, x=0, y=0, scale=1)

        # Calculate visible items (limited display space)
        max_visible = 4
        start_idx = max(0, min(selected_index - 1, len(items) - max_visible))

        for i in range(min(max_visible, len(items))):
            item_idx = start_idx + i
            if item_idx < len(items):
                prefix = ">" if item_idx == selected_index else " "
                y_pos = 16 + i * 12
                self.show_text(f"{prefix}{items[item_idx]}", x=0, y=y_pos)

    def show_pause_menu(self):
        """Display the pause menu."""
        self.clear()
        self.show_centered_text("PAUSED", y=10, scale=2)
        self.show_text("Press to quit", x=15, y=35)
        self.show_text("Any key: resume", x=10, y=50)

    def show_victory(self, score, moves=None, level=None):
        """
        Display victory screen.

        Args:
            score: Final score
            moves: Number of moves (optional)
            level: Level completed (optional)
        """
        self.clear()
        self.show_centered_text("VICTORY!", y=5, scale=2)
        if moves is not None:
            self.show_centered_text(f"Moves: {moves}", y=30)
        if level is not None:
            self.show_centered_text(f"Level: {level}", y=30)
        self.show_centered_text(f"Score: {score}", y=45)

    def show_time_remaining(self, seconds, x=70, y=0):
        """
        Display time remaining.

        Args:
            seconds: Seconds remaining
            x: X position
            y: Y position
        """
        self.show_text(f"Time: {int(seconds)}s", x=x, y=y)

    def update_label(self, label_obj, new_text):
        """
        Update an existing label's text.

        Args:
            label_obj: Label object returned from show_text
            new_text: New text string
        """
        if label_obj:
            label_obj.text = new_text

    def refresh(self):
        """
        Force a display refresh.
        Note: Usually not needed as display auto-refreshes.
        """
        self.display.refresh()
