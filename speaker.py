import pyttsx3
import winsound
import time
import threading
import queue

# ─────────────────────────────────────────
# pyttsx3 MUST run on its OWN dedicated
# thread — it uses a COM message loop on
# Windows and breaks if called from random
# threads.
# ─────────────────────────────────────────

_speech_queue = queue.Queue()
_last_spoken_time = 0
_engine = None


def _speech_worker():
    """Dedicated thread: owns the pyttsx3 engine and processes speak requests."""
    global _engine
    _engine = pyttsx3.init('sapi5')

    voices = _engine.getProperty('voices')

    # Pick a clear female voice if available, else first voice
    chosen = None
    for v in voices:
        if 'zira' in v.name.lower() or 'female' in v.name.lower():
            chosen = v.id
            break
    if not chosen and voices:
        chosen = voices[0].id
    if chosen:
        _engine.setProperty('voice', chosen)

    _engine.setProperty('rate', 160)   # words per minute
    _engine.setProperty('volume', 1.0) # max volume

    while True:
        text = _speech_queue.get()   # blocks until something to say
        if text is None:
            break
        try:
            _engine.stop()
            _engine.say(str(text))
            _engine.runAndWait()
        except Exception as e:
            print(f"[Speaker] TTS error: {e}")
        finally:
            _speech_queue.task_done()


# Start the dedicated speech thread at import time
_worker_thread = threading.Thread(target=_speech_worker, daemon=True)
_worker_thread.start()


# ─────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────

def speak(text, cooldown=2):
    """
    Queue text for speech. Enforces a cooldown so the same message
    isn't repeated within `cooldown` seconds.
    Safe to call from any thread.
    """
    global _last_spoken_time

    now = time.time()
    if now - _last_spoken_time < cooldown:
        return

    _last_spoken_time = now

    # Clear queue so stale messages don't pile up
    while not _speech_queue.empty():
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            break

    _speech_queue.put(str(text))


def set_rate(rate: int):
    """Change speaking speed (words per minute). Default 160."""
    if _engine:
        _engine.setProperty('rate', rate)


def set_volume(vol: float):
    """Set volume 0.0 – 1.0."""
    if _engine:
        _engine.setProperty('volume', max(0.0, min(1.0, vol)))


# ─────────────────────────────────────────
# ALERT BEEPS (winsound — non-blocking)
# ─────────────────────────────────────────

def beep_fast():
    """Short high-pitched beep — DANGER zone."""
    try:
        winsound.Beep(1500, 180)
    except Exception:
        pass


def beep_slow():
    """Lower longer beep — WARNING zone."""
    try:
        winsound.Beep(800, 380)
    except Exception:
        pass
