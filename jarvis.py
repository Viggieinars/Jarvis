import os
import openai
from dotenv import load_dotenv
import datetime
import time
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor
from threading import Timer
from speech import Speech
from ellab import ElevenLabsController
from spotify import SpotifyController
from weather import get_weather
from shopping_list import ShoppingList

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openweather_api_key = os.getenv('OPENWEATHER_API_KEY')

client = openai.OpenAI()
model = 'gpt-3.5-turbo-instruct'
name = 'Sir'
FANCY = False

executor = ThreadPoolExecutor(max_workers=2)
speech = Speech(name)
ellab = ElevenLabsController(name)
spotify = SpotifyController(name, FANCY)
shopping_list = ShoppingList(name, FANCY)

persistent_context = f"""
You are an AI assistant called Jarvis. You are talking to a user named {name}, who lives in Iceland and is a computer science student at Reykjavík University.
When addressing the user, use {name}. You are to speak with a posh british accent, like you are of royalty. Do NOT greet the user as you have already greeted him.
Right now, it is {datetime.datetime.now()}.
"""

# Maintain the last request and response
last_interaction = {"user": "", "ai": ""}

def clean_response(text):
    return text.strip().strip('-').strip()

def get_openai_response(prompt):
    conversation = (persistent_context + 
                    f"\nUser: {last_interaction['user']}\nAI: {last_interaction['ai']}\n" + 
                    f"User: {prompt}\nAI:")
    response = client.completions.create(
        model=model,
        prompt=conversation,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None
    )
    response_text = response.choices[0].text.strip()
    last_interaction['user'] = prompt
    last_interaction['ai'] = clean_response(response_text)
    return last_interaction['ai']

def listen_for_wake_word(source):
    print('Listening for "Jarvis"....')

    while True:
        audio = speech.recognizer.listen(source)
        try:
            text = speech.recognizer.recognize_google(audio)
            if 'jarvis' in text.lower() or 'wake up' in text.lower():
                print('Wake word detected')
                command = text.lower().split('jarvis', 1)[-1].strip()
                if command:
                    print(f'Command detected: {command}')
                    listen_and_respond(source, initial_prompt=command)
                else:
                    if not FANCY:
                        speech.speak_greeting()
                    else:
                        ellab.speak_greeting()
                    listen_and_respond(source)
                break
        except sr.UnknownValueError:
            print('Unable to recognize audio')
        except sr.WaitTimeoutError:
            continue

def listen_and_respond(source, initial_prompt=None):
    print('Listening for command...')

    if initial_prompt:
        handle_command(initial_prompt, source)
    
    while True:
        audio = speech.recognizer.listen(source, timeout=5, phrase_time_limit=5)
        try:
            text = speech.recognizer.recognize_google(audio)
            print(f'You said: {text}')
            if not text:
                continue

            handle_command(text, source)

        except sr.UnknownValueError:
            print('Unable to recognize audio')
            time.sleep(2)
        except sr.RequestError as e:
            print(f'Could not get request response: {e}')
            time.sleep(2)
        except sr.WaitTimeoutError:
            print('Listening timeout reached, please say something.')

def handle_command(text, source):
    if 'shopping list' in text.lower():
        if 'clear' in text.lower():
            shopping_list.clear_list()
            return
        else:
            shopping_list.check_list(source)
            return

    if 'play' in text.lower() or 'shuffle' in text.lower():
        spotify.play_music(text, source)
        listen_for_wake_word(source)
        return

    if 'stop music' in text.lower():
        spotify.pause_music()
        return

    if 'thanks' in text.lower() or 'thank you' in text.lower():
        if not FANCY:
            speech.speak_thanks()
        else:
            ellab.speak_thanks()
        return

    if 'goodbye' in text.lower() or 'shutdown' in text.lower():
        if not FANCY:
            speech.speak(f"Goodbye {name}, just call my name if you're in need of assistance")
        else:
            ellab.speak(f"Goodbye {name}, just call my name if you're in need of assistance")
        listen_for_wake_word(source)
        return

    if 'weather' in text.lower():
        city = text.split('in')[-1].strip() if 'in' in text else 'Reykjavik'
        weather_report = get_weather(city)
        if not FANCY:
            speech.speak(weather_report)
        else:
            ellab.speak(weather_report)
        return

    if 'set a timer' in text.lower() or 'wake me up in' in text.lower():
        set_timer(text.lower())
        return

    # Process OpenAI response in a separate thread
    future_response = executor.submit(get_openai_response, text)
    response_text = future_response.result()
    print(f'AI response: {response_text}')
    if not FANCY:
        speech.speak(response_text)
    else:
        ellab.speak(response_text)
    # Continue listening for more commands
    listen_and_respond(source)

def set_timer(command):
    import re
    match = re.search(r'(set a timer for|wake me up in) (\d+) (hour|hours|minute|minutes|second|seconds)', command)
    if not match:
        speech.speak("Sorry, I couldn't understand the timer duration.")
        return

    duration = int(match.group(2))
    unit = match.group(3)
    if 'second' in unit:
        duration_seconds = duration
    elif 'minute' in unit:
        duration_seconds = duration * 60
    elif 'hour' in unit:
        duration_seconds = duration * 3600

    speech.speak(f"Setting a timer for {duration} {unit}.")
    Timer(duration_seconds, timer_finished).start()

def timer_finished():
    speech.speak("Time's up!")

if __name__ == "__main__":
    with sr.Microphone() as source:
        listen_for_wake_word(source)
