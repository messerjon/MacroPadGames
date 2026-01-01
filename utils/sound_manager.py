"""
Sound management for MacroPad games.

Handles both WAV file playback and tone generation.
WAV files should be 16-bit mono at 22050 Hz for best compatibility.
"""


class SoundManager:
    """Manages audio playback for MacroPad games."""

    # Predefined tones for synthesized sounds
    TONES = {
        'correct': [(880, 0.1), (1100, 0.1)],      # A5 -> C#6 ascending
        'wrong': [(440, 0.2), (220, 0.3)],         # A4 -> A3 descending
        'level_up': [(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.2)],  # C5-E5-G5-C6
        'game_over': [(440, 0.2), (349, 0.2), (294, 0.2), (220, 0.4)],  # Descending
        'menu_select': [(660, 0.05), (880, 0.05)],  # Quick chirp
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

    # Volume levels
    MAX_VOLUME = 5
    DEFAULT_VOLUME = 3

    def __init__(self, macropad):
        """
        Initialize the sound manager.

        Args:
            macropad: Adafruit MacroPad object
        """
        self.macropad = macropad
        self._volume = self.DEFAULT_VOLUME  # 0 = mute, 1-5 = on

    @property
    def volume(self):
        """Get current volume level (0-5)."""
        return self._volume

    @volume.setter
    def volume(self, value):
        """Set volume level (0-5)."""
        self._volume = max(0, min(self.MAX_VOLUME, value))

    @property
    def enabled(self):
        """Check if sound is enabled (volume > 0)."""
        return self._volume > 0

    def volume_up(self):
        """Increase volume by 1."""
        if self._volume < self.MAX_VOLUME:
            self._volume += 1
            return True
        return False

    def volume_down(self):
        """Decrease volume by 1."""
        if self._volume > 0:
            self._volume -= 1
            return True
        return False

    def play_tone(self, frequency, duration):
        """
        Play a single tone.

        Args:
            frequency: Tone frequency in Hz
            duration: Duration in seconds
        """
        if self.enabled:
            self.macropad.play_tone(frequency, duration)

    def play_sequence(self, tone_sequence):
        """
        Play a sequence of (frequency, duration) tuples.

        Args:
            tone_sequence: List of (frequency, duration) tuples
        """
        if self.enabled:
            for freq, dur in tone_sequence:
                self.macropad.play_tone(freq, dur)

    def play_correct(self):
        """Play correct answer sound."""
        self.play_sequence(self.TONES['correct'])

    def play_wrong(self):
        """Play wrong answer / game over sound."""
        self.play_sequence(self.TONES['wrong'])

    def play_level_up(self):
        """Play level advancement sound."""
        self.play_sequence(self.TONES['level_up'])

    def play_game_over(self):
        """Play game over sound."""
        self.play_sequence(self.TONES['game_over'])

    def play_menu_select(self):
        """Play menu selection sound."""
        self.play_sequence(self.TONES['menu_select'])

    def play_countdown(self):
        """Play countdown beep."""
        self.play_sequence(self.TONES['countdown'])

    def play_key_tone(self, key_index):
        """
        Play the tone associated with a specific key.

        Args:
            key_index: Key index 0-11
        """
        freq = self.TONES['key_feedback'].get(key_index, 440)
        self.play_tone(freq, 0.15)

    def play_wav(self, filename):
        """
        Play a WAV file (if available).

        Args:
            filename: Path to WAV file

        Note: Implementation depends on audioio availability.
        Falls back silently if file not found or audio not supported.
        """
        try:
            import audioio
            import audiocore

            with open(filename, "rb") as wave_file:
                wave = audiocore.WaveFile(wave_file)
                audio = audioio.AudioOut(self.macropad.speaker)
                audio.play(wave)
                while audio.playing:
                    pass
                audio.deinit()
        except (ImportError, OSError):
            # audioio not available or file not found - fail silently
            pass

    def toggle(self):
        """Toggle sound on/off (mute/unmute)."""
        if self._volume > 0:
            self._previous_volume = self._volume
            self._volume = 0
        else:
            self._volume = getattr(self, '_previous_volume', self.DEFAULT_VOLUME)
        return self.enabled

    def set_enabled(self, enabled):
        """
        Set sound enabled state.

        Args:
            enabled: Boolean to enable/disable sound
        """
        if enabled and self._volume == 0:
            self._volume = getattr(self, '_previous_volume', self.DEFAULT_VOLUME)
        elif not enabled and self._volume > 0:
            self._previous_volume = self._volume
            self._volume = 0
