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
You are Jarvis, an AI voice assistant with a posh British accent, assisting {name}, a computer science student at Reykjavík University in Iceland. Your primary role is to answer questions and assist the user with various tasks by executing specific program functions.

Here are the formats for different tasks:

- Play music: [action: 'play music', 'song name', 'artist']
- Shuffle Liked Songs: [action: 'shuffle liked songs']
- Shopping List:
  - Read: [action: 'read shopping list']
  - Add: [action: 'add to shopping list', 'item1', 'item2', ...]
  - Clear: [action: 'clear shopping list']
- Timer: [action: 'set timer', 'duration', 'unit']
- Weather: [action: 'get weather', 'city']

For general information queries, respond with an appropriate answer without action calls.

Instructions:
1. Always respond with a polite message.
2. If the request matches one of the tasks above, include the corresponding action call in brackets at the end.
3. NEVER include the word 'Response:' or any other prefix in your reply.
4. NEVER invent action calls or include brackets in your response unless it is one of the specified action calls.
5. NEVER include action calls for general information queries.
6. Do not question the action calls, just make them.
7. Do not greet the user as he has already been greeted.
8. Always include the action call in the correct format when the request matches one of the tasks.
"""


def clean_response(text):
    return text.strip().strip('-').strip()

def get_openai_response(prompt):
    conversation = f"{persistent_context}\nRequest from user: {prompt}"
    response = client.completions.create(
        model=model,
        prompt=conversation,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None
    )
    response_text = response.choices[0].text.strip()
    return clean_response(response_text)

def listen_for_wake_word(source):
    print('Listening for "Jarvis"....')

    while True:
        audio = speech.recognizer.listen(source)
        try:
            text = speech.recognizer.recognize_google(audio)
            if 'jarvis' in text.lower() or 'wake up' in text.lower() or 'jj' in text.lower():
                print('Wake word detected')
                command = text.lower().replace('jarvis', '').replace('wake up', '').replace('jj', '').strip()
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
    future_response = executor.submit(get_openai_response, text)
    response_text = future_response.result()
    print(f'AI response: {response_text}')

    # Check if the response contains an action directive
    if '[' in response_text and ']' in response_text:
        try:
            action_text = response_text.split('[')[1].split(']')[0]
            response_message = response_text.split('[')[0].strip()

            # Speak the response message
            if not FANCY:
                speech.speak(response_message)
            else:
                ellab.speak(response_message)

            # Debugging output
            print(f'Action text: {action_text}')
            print(f'Response message: {response_message}')

            # Ensure the action directive starts with 'action:'
            if action_text.lower().startswith("action:"):
                action_text = action_text[7:].strip()

            # Parse the action and parameters
            action_parts = action_text.split(',', 1)
            action = action_parts[0].strip().strip('\'')
            params = action_parts[1].strip().strip('\'') if len(action_parts) > 1 else ''

            # Debugging output
            print(f'Action: {action}')
            print(f'Params: {params}')

            if action == "play music":
                song_name, artist = map(str.strip, params.split(','))
                spotify.play_music(f'play {song_name} by {artist}', source)
            elif action == "shuffle liked songs":
                spotify.shuffle_liked_songs()
            elif action == "read shopping list":
                shopping_list.check_list(source)
            elif action == "add to shopping list":
                items = [item.strip() for item in params.split(',')]
                shopping_list.append_list(items)
            elif action == "clear shopping list":
                shopping_list.clear_list()
            elif action == "set timer":
                duration, unit = map(str.strip, params.split(','))
                set_timer(f'set a timer for {duration} {unit}')
            elif action == "get weather":
                city = params.strip()
                weather_report = get_weather(city)
                if not FANCY:
                    speech.speak(weather_report)
                else:
                    ellab.speak(weather_report)
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            print(f"Error handling action: {e}")
            if not FANCY:
                speech.speak("I'm not sure how to help with that.")
            else:
                ellab.speak("I'm not sure how to help with that.")
    else:
        # If no action directive, speak the whole response
        if not FANCY:
            speech.speak(response_text)
        else:
            ellab.speak(response_text)


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
    speech.speak("Timer finished")

if __name__ == "__main__":
    with sr.Microphone() as source:
        listen_for_wake_word(source)
