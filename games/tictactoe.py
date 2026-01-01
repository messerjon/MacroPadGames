"""
Tic-Tac-Toe game for MacroPad.

Classic 2-player game using the bottom 3x3 keys (3-11).
Player 1 is RED (X), Player 2 is BLUE (O).
Take turns pressing keys to claim squares.
"""

import time
from .base_game import BaseGame


class TicTacToe(BaseGame):
    """Tic-Tac-Toe - Two player classic!"""

    NAME = "Tic-Tac-Toe"
    DESCRIPTION = "2 player classic!"

    # Use bottom 9 keys (3-11) for 3x3 grid
    # Layout:
    #  (0) (1) (2)   <- not used
    #   3   4   5    <- row 0
    #   6   7   8    <- row 1
    #   9  10  11    <- row 2

    GRID_KEYS = [3, 4, 5, 6, 7, 8, 9, 10, 11]

    # Winning combinations (indices into GRID_KEYS)
    WIN_COMBOS = [
        [0, 1, 2],  # Top row
        [3, 4, 5],  # Middle row
        [6, 7, 8],  # Bottom row
        [0, 3, 6],  # Left column
        [1, 4, 7],  # Middle column
        [2, 5, 8],  # Right column
        [0, 4, 8],  # Diagonal
        [2, 4, 6],  # Anti-diagonal
    ]

    # Colors
    PLAYER1_COLOR = (255, 0, 0)    # Red for Player 1 (X)
    PLAYER2_COLOR = (0, 0, 255)    # Blue for Player 2 (O)
    EMPTY_COLOR = (30, 30, 30)     # Dim for empty
    WIN_COLOR = (0, 255, 0)        # Green for winning line
    INDICATOR_P1 = (255, 50, 50)   # Indicator for P1 turn
    INDICATOR_P2 = (50, 50, 255)   # Indicator for P2 turn

    def __init__(self, macropad, sound_manager, led_manager, display_manager):
        """Initialize Tic-Tac-Toe game."""
        super().__init__(macropad, sound_manager, led_manager, display_manager)
        self.board = [0] * 9  # 0=empty, 1=player1, 2=player2
        self.current_player = 1
        self.game_active = False
        self.games_played = 0
        self.p1_wins = 0
        self.p2_wins = 0
        self.draws = 0

    def start(self):
        """Initialize game."""
        print(f"[DEBUG] {self.NAME}.start() called")
        self.reset()

        # Show instructions
        self.display.clear()
        self.display.show_title(self.NAME)
        time.sleep(0.5)
        self.display.clear()
        self.display.show_text("2 Players!", x=30, y=10)
        self.display.show_text("RED vs BLUE", x=25, y=25)
        self.display.show_text("Use bottom 9 keys", x=5, y=45)
        time.sleep(2.5)

        self.is_running = True
        print(f"[DEBUG] {self.NAME}.start() complete")
        self._start_new_game()

    def _start_new_game(self):
        """Start a new game round."""
        self.board = [0] * 9
        self.current_player = 1
        self.game_active = True
        self.games_played += 1

        self._update_display()
        self._render_board()

    def _render_board(self):
        """Render the game board on LEDs."""
        self.leds.clear_all()

        # Show grid
        for i, key in enumerate(self.GRID_KEYS):
            if self.board[i] == 1:
                self.leds.set_key(key, self.PLAYER1_COLOR)
            elif self.board[i] == 2:
                self.leds.set_key(key, self.PLAYER2_COLOR)
            else:
                self.leds.set_key(key, self.EMPTY_COLOR)

        # Show current player indicator on top row
        if self.game_active:
            if self.current_player == 1:
                self.leds.set_key(0, self.INDICATOR_P1)
            else:
                self.leds.set_key(2, self.INDICATOR_P2)

    def _update_display(self):
        """Update the OLED display."""
        self.display.clear()
        self.display.show_text("TIC-TAC-TOE", x=20, y=0)

        if self.game_active:
            if self.current_player == 1:
                self.display.show_text("RED's turn", x=30, y=25)
            else:
                self.display.show_text("BLUE's turn", x=25, y=25)

        self.display.show_text(f"R:{self.p1_wins} B:{self.p2_wins} D:{self.draws}", x=10, y=52)

    def update(self):
        """Main game loop."""
        if not self.is_running:
            return False

        if self.game_active:
            # Handle key presses
            key_event = self.macropad.keys.events.get()
            if key_event and key_event.pressed:
                self.handle_key_press(key_event.key_number)

        # Check for exit
        self.macropad.encoder_switch_debounced.update()
        if self.macropad.encoder_switch_debounced.pressed:
            self.is_running = False
            return False

        return self.is_running

    def handle_key_press(self, key_index):
        """Handle key press."""
        if not self.game_active:
            # Start new game on any press
            self._start_new_game()
            return

        # Check if valid grid key
        if key_index not in self.GRID_KEYS:
            # Top row keys - just flash
            self.leds.flash_key(key_index, 'white', times=1, on_time=0.1, off_time=0)
            return

        # Get grid index
        grid_idx = self.GRID_KEYS.index(key_index)

        # Check if empty
        if self.board[grid_idx] != 0:
            # Already taken
            self.sound.play_tone(200, 0.1)
            return

        # Make move
        self.board[grid_idx] = self.current_player

        # Play sound
        if self.current_player == 1:
            self.sound.play_tone(440, 0.1)
        else:
            self.sound.play_tone(330, 0.1)

        # Check for win
        winner = self._check_winner()
        if winner:
            self._handle_win(winner)
            return

        # Check for draw
        if 0 not in self.board:
            self._handle_draw()
            return

        # Switch player
        self.current_player = 2 if self.current_player == 1 else 1
        self._update_display()
        self._render_board()

    def _check_winner(self):
        """Check if there's a winner. Returns winner (1 or 2) or None."""
        for combo in self.WIN_COMBOS:
            a, b, c = combo
            if self.board[a] != 0 and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def _get_winning_combo(self, winner):
        """Get the winning combination indices."""
        for combo in self.WIN_COMBOS:
            a, b, c = combo
            if self.board[a] == winner and self.board[b] == winner and self.board[c] == winner:
                return combo
        return []

    def _handle_win(self, winner):
        """Handle a win."""
        self.game_active = False

        if winner == 1:
            self.p1_wins += 1
            win_text = "RED WINS!"
            self.sound.play_correct()
        else:
            self.p2_wins += 1
            win_text = "BLUE WINS!"
            self.sound.play_correct()

        # Flash winning line
        combo = self._get_winning_combo(winner)
        for _ in range(3):
            for idx in combo:
                self.leds.set_key(self.GRID_KEYS[idx], self.WIN_COLOR)
            time.sleep(0.3)
            self._render_board()
            time.sleep(0.2)

        # Show result
        self.display.clear()
        self.display.show_centered_text(win_text, y=15, scale=2)
        self.display.show_text("Press to play again", x=0, y=45)

        time.sleep(0.5)

    def _handle_draw(self):
        """Handle a draw."""
        self.game_active = False
        self.draws += 1

        self.leds.flash_all('yellow', times=2, on_time=0.2, off_time=0.2)

        self.display.clear()
        self.display.show_centered_text("DRAW!", y=15, scale=2)
        self.display.show_text("Press to play again", x=0, y=45)

    def reset(self):
        """Reset game state."""
        self.board = [0] * 9
        self.current_player = 1
        self.game_active = False
        self.games_played = 0
        self.p1_wins = 0
        self.p2_wins = 0
        self.draws = 0
        self.score = 0
        self.is_running = False
        self.game_over = False
        self.leds.clear_all()
