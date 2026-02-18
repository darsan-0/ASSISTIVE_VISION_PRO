import pyttsx3
import winsound
import time

# ------------------------------
# INIT WINDOWS SPEECH ENGINE
# ------------------------------
engine = pyttsx3.init('sapi5')   # Windows speech API

# Select available system voice safely
voices = engine.getProperty('voices')

# If multiple voices exist use first one safely
if len(voices) > 0:
    engine.setProperty('voice', voices[0].id)

engine.setProperty('rate', 160)  # speaking speed

# Cooldown control to avoid repeated speaking
last_spoken_time = 0


# ------------------------------
# SPEAK FUNCTION
# ------------------------------
def speak(text, cooldown=2):
    global last_spoken_time

    try:
        # prevent too frequent speech
        if time.time() - last_spoken_time < cooldown:
            return

        last_spoken_time = time.time()

        engine.stop()              # clear previous speech queue
        engine.say(str(text))
        engine.runAndWait()

    except Exception as e:
        print("Speaker Error:", e)


# ------------------------------
# ALERT SOUNDS
# ------------------------------
def beep_fast():
    try:
        winsound.Beep(1500, 200)
    except:
        pass


def beep_slow():
    try:
        winsound.Beep(800, 400)
    except:
        pass
