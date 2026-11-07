"""
Audio feedback, electronic chimes, and optional voice assistance for Apex Federal Bank ATM.
"""

import queue
import threading
from typing import Optional

try:
    import winsound
except ImportError:
    winsound = None


class AudioSpeaker:
    """Provides authentic ATM audio cues, keypad clicks, and optional synthesized voice prompts."""

    def __init__(self, tts_enabled: bool = True):
        self.muted = False
        self.tts_enabled = tts_enabled
        self._speech_queue: queue.Queue[str] = queue.Queue()
        self._engine = None
        self._has_engine = False

        if self.tts_enabled:
            # Initialize TTS worker thread
            worker = threading.Thread(target=self._tts_worker, daemon=True)
            worker.start()

    def _init_tts(self) -> None:
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', 160)
            self._has_engine = True
        except Exception:
            self._has_engine = False

    def _tts_worker(self) -> None:
        self._init_tts()
        while True:
            text = self._speech_queue.get()
            if text and self._has_engine and not self.muted:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception:
                    pass
            self._speech_queue.task_done()

    def speak(self, text: str) -> None:
        """Enqueues a voice prompt for asynchronous speaking."""
        if not self.muted and self.tts_enabled:
            self._speech_queue.put(text)

    def play_key_beep(self) -> None:
        """Subtle mechanical click tone for ATM keypad presses."""
        if self.muted or not winsound:
            return
        threading.Thread(target=self._beep, args=(1800, 25), daemon=True).start()

    def play_success_chime(self) -> None:
        """Pleasant two-tone chime for completed transactions."""
        if self.muted or not winsound:
            return
        def _chime():
            self._beep(1200, 70)
            self._beep(1600, 110)
        threading.Thread(target=_chime, daemon=True).start()

    def play_error_tone(self) -> None:
        """Low-pitch alert for invalid PIN or rejected operations."""
        if self.muted or not winsound:
            return
        def _alert():
            self._beep(450, 150)
            self._beep(350, 220)
        threading.Thread(target=_alert, daemon=True).start()

    def play_cash_chime(self) -> None:
        """Mechanical gear pulse cue for cash dispensing."""
        if self.muted or not winsound:
            return
        def _dispense():
            for _ in range(4):
                self._beep(800, 30)
            self._beep(1400, 100)
        threading.Thread(target=_dispense, daemon=True).start()

    def _beep(self, freq: int, duration: int) -> None:
        try:
            if winsound:
                winsound.Beep(freq, duration)
        except Exception:
            pass

    def toggle_mute(self) -> bool:
        """Toggles audio mute state and returns new state (True = muted)."""
        self.muted = not self.muted
        return self.muted
