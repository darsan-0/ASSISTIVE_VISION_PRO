"""
voice_commands.py — Voice Command Listener
============================================
Listens to microphone in a background thread.
Recognized commands trigger actions via callbacks.

Supported commands:
  START / ACTIVATE          → start detection
  STOP / PAUSE / DEACTIVATE → stop detection
  FRONT / WHAT'S AHEAD      → describe objects in front
  BACK / BEHIND             → describe objects behind (future)
  LEFT                      → describe objects on the left
  RIGHT                     → describe objects on the right
  STATUS / REPORT           → full scene summary
  REPEAT                    → repeat last guidance
  MUTE / SILENCE            → mute voice output
  UNMUTE / SOUND ON         → unmute voice output
  HELP                      → list available commands
  EXIT / QUIT               → exit app
"""

import threading
import time

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("[VoiceCmd] speech_recognition not installed. Run: pip install SpeechRecognition pyaudio")


# ─────────────────────────────────────────────
# Command keyword map  →  action key
# ─────────────────────────────────────────────
COMMAND_MAP = {
    # Start
    "start":        "start",
    "activate":     "start",
    "begin":        "start",
    "on":           "start",

    # Stop
    "stop":         "stop",
    "pause":        "stop",
    "deactivate":   "stop",
    "off":          "stop",
    "halt":         "stop",

    # Directions
    "front":        "front",
    "ahead":        "front",
    "forward":      "front",
    "what's ahead": "front",
    "whats ahead":  "front",

    "back":         "back",
    "behind":       "back",
    "backward":     "back",

    "left":         "left",
    "move left":    "left",

    "right":        "right",
    "move right":   "right",

    # Status
    "status":       "status",
    "report":       "status",
    "scan":         "status",
    "describe":     "status",
    "what do you see": "status",
    "what's around":   "status",

    # Repeat
    "repeat":       "repeat",
    "say again":    "repeat",
    "again":        "repeat",

    # Mute
    "mute":         "mute",
    "silence":      "mute",
    "quiet":        "mute",

    # Unmute
    "unmute":       "unmute",
    "sound on":     "unmute",
    "voice on":     "unmute",

    # Help
    "help":         "help",
    "commands":     "help",
    "what can you do": "help",

    # Exit
    "exit":         "exit",
    "quit":         "exit",
    "close":        "exit",
}


# ─────────────────────────────────────────────
# VoiceCommandListener
# ─────────────────────────────────────────────
class VoiceCommandListener:
    """
    Continuously listens to microphone and fires on_command(action, raw_text)
    whenever a known command is detected.

    Usage:
        def my_handler(action, text):
            print(f"Command: {action}  (heard: '{text}')")

        listener = VoiceCommandListener(on_command=my_handler)
        listener.start()
    """

    def __init__(self, on_command=None, on_listening=None, language="en-US"):
        self.on_command  = on_command   # callback(action: str, raw: str)
        self.on_listening = on_listening  # callback(state: bool)  True=listening, False=processing
        self.language    = language
        self.active      = False
        self._thread     = None
        self._recognizer = None
        self._mic        = None

    def start(self):
        if not SR_AVAILABLE:
            print("[VoiceCmd] Cannot start — speech_recognition not available.")
            return
        if self.active:
            return
        self.active = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        print("[VoiceCmd] Listening for voice commands…")

    def stop(self):
        self.active = False

    def _listen_loop(self):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300        # sensitivity to ambient noise
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.7         # seconds of silence = end of phrase

        try:
            mic = sr.Microphone()
        except OSError:
            print("[VoiceCmd] No microphone found.")
            return

        # Calibrate to ambient noise once at startup
        with mic as source:
            print("[VoiceCmd] Calibrating to ambient noise… (1 sec)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[VoiceCmd] Ready. Speak a command.")

        while self.active:
            try:
                if self.on_listening:
                    self.on_listening(True)

                with mic as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=4)

                if self.on_listening:
                    self.on_listening(False)

                # Recognize using Google free API (online)
                try:
                    raw = recognizer.recognize_google(audio, language=self.language).lower().strip()
                    print(f"[VoiceCmd] Heard: '{raw}'")
                    action = self._match_command(raw)
                    if action and self.on_command:
                        self.on_command(action, raw)
                    elif not action:
                        print(f"[VoiceCmd] No matching command for: '{raw}'")

                except sr.UnknownValueError:
                    pass  # couldn't understand
                except sr.RequestError as e:
                    print(f"[VoiceCmd] Google STT error: {e}")
                    # fallback: try offline sphinx if available
                    try:
                        raw = recognizer.recognize_sphinx(audio).lower().strip()
                        action = self._match_command(raw)
                        if action and self.on_command:
                            self.on_command(action, raw)
                    except Exception:
                        pass

            except sr.WaitTimeoutError:
                pass  # no speech detected in timeout window, loop again
            except Exception as e:
                print(f"[VoiceCmd] Listener error: {e}")
                time.sleep(1)

    def _match_command(self, text):
        """Match raw text against command map. Longest match wins."""
        best_action = None
        best_len = 0
        for phrase, action in COMMAND_MAP.items():
            if phrase in text and len(phrase) > best_len:
                best_action = action
                best_len = len(phrase)
        return best_action


# ─────────────────────────────────────────────
# Help text
# ─────────────────────────────────────────────
HELP_TEXT = (
    "Available commands: "
    "start, stop, front, back, left, right, "
    "status, repeat, mute, unmute, help, exit."
)
