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

    def check_list(self, source):
        try:
            with open("shopping_list.txt", "r") as file:
                contents = file.read().strip()
                if not contents:
                    self._speak('The shopping list is currently empty, do you want to add to it?')
                    audio = self.speech.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        response = self.speech.recognizer.recognize_google(audio)
                        if 'yes' in response.lower():
                            self.append_list(source)
                        else:
                            self._speak('Okay, let me know if you need anything else.')
                            return
                    except sr.UnknownValueError:
                        self._speak('I did not catch that. Please say yes or no')
                    except sr.WaitTimeoutError:
                        self._speak('Listening timeout reached, please say something.')
                else:
                    items = contents.split('\n')  # Initialize items with the contents of the shopping list
                    self._speak('Your shopping list contains the following items:')
                    for item in items:
                        self._speak(item)
                    self._speak('Do you want to add more items to the shopping list?')
                    audio = self.speech.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        response = self.speech.recognizer.recognize_google(audio)
                        if 'yes' in response.lower():
                            self.append_list(source)
                        else:
                            self._speak('Okay, let me know if you need anything else.')
                            return
                    except sr.UnknownValueError:
                        self._speak('I did not catch that. Please say yes or no.')
                    except sr.WaitTimeoutError:
                        self._speak('Listening timeout reached, please say something.')
        except FileNotFoundError:
            self._speak('The shopping list is currently empty, do you want to add to it?')
            audio = self.speech.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            try:
                response = self.speech.recognizer.recognize_google(audio)
                if 'yes' in response.lower():
                    self.append_list(source)
                else:
                    self._speak('Okay, let me know if you need anything else.')
                    return
            except sr.UnknownValueError:
                self._speak('I did not catch that. Please say yes or no.')
            except sr.WaitTimeoutError:
                self._speak('Listening timeout reached, please say something.')

    def append_list(self, source):
        self._speak('Ready to add to the shopping list. Please say the items one by one, followed by the word "done" or "that\'s it".')
        items = []
        while True:
            audio = self.speech.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            try:
                text = self.speech.recognizer.recognize_google(audio)
                print(f'You said: {text}')
                if 'done' in text.lower() or "that's it" in text.lower():
                    break
                items.append(text.strip())
                self._speak('Yes?')
            except sr.UnknownValueError:
                self._speak('I did not catch that. Please say the item again.')
            except sr.WaitTimeoutError:
                self._speak('It seems you are not speaking. Please say the item again.')

        print(f'Final items to add: {items}')

        with open("shopping_list.txt", "a") as file:
            for item in items:
                file.write(f"{item}\n")
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
