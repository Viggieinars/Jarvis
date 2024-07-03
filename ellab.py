from elevenlabs.client import ElevenLabs
from elevenlabs import play, Voice
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

class ElevenLabsController:
    def __init__(self, name):
        self.name = name
        self.client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
        self.all_voices = self.client.voices.get_all()
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


    def speak(self, input_text, voice_id='rWV5HleMkWb5oluMwkA7'):
        
        audio = self.client.generate(
            text=input_text,
            voice=Voice(
                voice_id=voice_id))
        play(audio)

    def speak_greeting(self):
        self.speak(np.random.choice(self.greetings))

    def speak_thanks(self):
        self.speak(np.random.choice(self.thanks_responses))
