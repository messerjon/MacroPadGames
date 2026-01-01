# Games package for MacroPad Games
from .base_game import BaseGame
from .speed_chase import SpeedChase
from .simon_says import SimonSays
from .whack_a_mole import WhackAMole
from .color_match import ColorMatch
from .memory_grid import MemoryGrid
from .lights_out import LightsOut
from .reaction_timer import ReactionTimer
from .piano import Piano
from .pattern_copy import PatternCopy
from .hot_potato import HotPotato
from .tictactoe import TicTacToe

__all__ = [
    'BaseGame',
    'SpeedChase',
    'SimonSays',
    'WhackAMole',
    'ColorMatch',
    'MemoryGrid',
    'LightsOut',
    'ReactionTimer',
    'Piano',
    'PatternCopy',
    'HotPotato',
    'TicTacToe',
]
