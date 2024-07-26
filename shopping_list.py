import os
import speech_recognition as sr
from speech import Speech
from ellab import ElevenLabsController

class ShoppingList:
    def __init__(self, name, fancy_voice):
        self.name = name
        self.speech = Speech(name)
        self.ellab = ElevenLabsController(name)
        self.fancy_voice = fancy_voice

    def check_list(self):
        try:
            with open("shopping_list.txt", "r") as file:
                contents = file.read().strip()
                if not contents:
                    self._speak('The shopping list is currently empty.')
                else:
                    items = contents.split('\n')
                    self._speak('Your shopping list contains the following items:')
                    for item in items:
                        self._speak(item)
        except FileNotFoundError:
            self._speak('The shopping list is currently empty.')

    def add_items(self, items):
        with open("shopping_list.txt", "a") as file:
            for item in items:
                file.write(f"{item.replace("'", "")}\n")
                print(f'Added: {item}')
        self._speak('Items added to the shopping list.')

    def clear_list(self):
        with open("shopping_list.txt", "w") as file:
            file.write("")
        self._speak('The shopping list has been cleared.')

    def _speak(self, text):
        if not self.fancy_voice:
            self.speech.speak(text)
        else:
            self.ellab.speak(text)
