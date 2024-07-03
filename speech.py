import pyttsx3
import speech_recognition as sr
import numpy as np

class Speech:
    def __init__(self, name):
        self.name = name
        self.engine = pyttsx3.init()
        voice = self.engine.getProperty('voices')[14]
        self.engine.setProperty('voice', voice.id)
        self.recognizer = sr.Recognizer()

        self.greetings = [
            f'Yes {self.name}?',
            f'Hello {self.name}',
            f'Greetings {self.name}',
            f'Salutations {self.name}',
            f'Ready for assistance {self.name}',
            f'Welcome home {self.name}',
            f'Yes {self.name}, how can I help?',
            f'What can I do for you {self.name}'
        ]

        self.thanks_responses = [
            f"It's what I'm here for {self.name}",
            f"It is my pleasure {self.name}",
            f"Well I thank you for my existence {self.name}",
            f"I'm glad to be a help to you {self.name}",
            f"You're welcome {self.name}, do you need anything else?",
        ]

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def speak_greeting(self):
        self.speak(np.random.choice(self.greetings))

    def speak_thanks(self):
        self.speak(np.random.choice(self.thanks_responses))

