
import pyttsx3
import winsound

engine = pyttsx3.init()
engine.setProperty('rate', 160)


def speak(text):
    engine.say(text)
    engine.runAndWait()


def beep_fast():
    winsound.Beep(1500, 200)


def beep_slow():
    winsound.Beep(800, 400)
