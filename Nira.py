# MIT License
# Copyright (c) 2024 NightBlobby
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import tkinter as tk
from tkinter import ttk, font, messagebox
import speech_recognition as sr
import pyttsx3
import threading
import datetime
import webbrowser
import requests
import time
import random
import asyncio
import requests
from bleak import BleakScanner, BleakClient
from plyer import notification
import nfc
import os
import smtplib
from email.message import EmailMessage
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
import pyowm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PyDictionary import PyDictionary
import hashlib
import cv2
import tensorflow as tf
import numpy as np
import asyncio
from newsapi import NewsApiClient
import google.generativeai as genai
from utils.responses import greetings, thank_responses, compliments, hate_comments, thanks, farewell_responses, farewells, wellbeing_inquiries, wellbeing_responses, responses_negative, responses_compliments

# Ensure you have StableLM installed
genai.configure(api_key='AIzaSyBQoZazKr7rCgAz1ikAVJcL-z4necM6ZpY')
model = genai.GenerativeModel('gemini-1.5-pro-latest')
chat = model.start_chat()

# Creator/AI name
assistant_name = "Nira"
creator_name = "Blobby"

# Download NLTK resources if not already downloaded
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

engine = pyttsx3.init()
# List available voices
voices = engine.getProperty('voices')
for voice in voices:
    print(f"Voice: {voice.id}")

# Set the voice ID you want to use
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.karen')

recognizer = sr.Recognizer()

# Initialize currency converter
currency_converter = CurrencyRates()
btc_converter = BtcConverter()

# Initialize weather API with your API key
owm = pyowm.OWM('YOUAPI')  # Replace with your OpenWeatherMap API key

# Initialize Spotify API (Replace placeholders with your credentials)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="YOUR_REDIRECT_URI",
                                               scope="user-read-playback-state,user-modify-playback-state"))

# Initialize PyDictionary
dictionary = PyDictionary()

# Function to greet the user based on the time of day
def greet_user():
    """Greet the user based on the current time of day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        speak("Good morning! How can I assist you today?")
    elif 12 <= hour < 17:
        speak("Good afternoon! How can I assist you today?")
    elif 17 <= hour < 20:
        speak("Good evening! How can I assist you today?")
    else:
        speak("Good night! How can I assist you today?")

    # Add personalized compliments or acknowledgments here
    speak(f"I am {assistant_name}, your personal assistant.")
    now = datetime.datetime.now()
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}, and the time is {now.strftime('%I:%M %p')}.")

class NLPModel:
    """A class for handling NLP model operations."""
    def __init__(self):
        self.model = make_pipeline(StandardScaler(), SVC())
        self.load_model()

    def load_model(self):
        """Load the NLP model."""
        try:
            self.model = joblib.load('nlp_model.pkl')
        except FileNotFoundError:
            # Train or load your NLP model here
            pass

    def predict_intent(self, text):
        """Predict the intent of the given text."""
        return self.model.predict([text])[0]

nlp_model = NLPModel()

# Function to speak
def speak(text):
    """Speak the given text using the text-to-speech engine."""
    output = f"{assistant_name}: {text}"
    print(output)
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's command
def listen(input_method):
    """Listen to the user's command based on the input method."""
    if input_method == "text":
        return listen_text()
    elif input_method == "voice":
        return listen_voice()
    else:
        speak("Invalid input method selected.")
        return None

# Function to listen to the user's command via text input
def listen_text():
    """Listen to the user's command via text input."""
    command = input("Enter your command: ")
    print(f"You said: {command}")
    return command

# Function to listen to the user's command via voice input
def listen_voice():
    """Listen to the user's command via voice input."""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Could you repeat?")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return None
    except Exception as e:
        speak(f"An error occurred: {e}")
        return None

# Function to fetch weather information for a given city
def get_weather(city_name):
    """Fetch weather information for a given city."""
    try:
        observation = owm.weather_manager().weather_at_place(city_name)
        weather = observation.weather
        temperature = weather.temperature('celsius')['temp']
        status = weather.detailed_status
        weather_info = f"{city_name}: {temperature}°C, {status}"
        return weather_info
    except Exception as e:
        return f"Could not get weather information. Error: {e}"

# Function to fetch a joke from an online API
def fetch_joke():
    """Fetch a joke from an online API."""
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:
        joke_data = response.json()
        return f"{joke_data['setup']}... {joke_data['punchline']}"
    else:
        jokes = ["Why don't scientists trust atoms? Because they make up everything!",
                 "What do you get if you cross a cat with a dark horse? Kitty Perry.",
                 "Why don't some couples go to the gym? Because some relationships don't work out.",
                 "It told my wife she was drawing her eyebrows too high. She looked surprised."]
        return random.choice(jokes)

# Function to set a timer
def set_timer(duration_seconds):
    """Set a timer for the given duration in seconds."""
    def timer_thread():
        time.sleep(duration_seconds)
        speak("Time's up!")

    thread = threading.Thread(target=timer_thread)
    thread.start()

# Function to set an alarm
def set_alarm(alarm_time):
    """Set an alarm for the given time."""
    def alarm_thread():
        while True:
            current_time = datetime.datetime.now().strftime('%H:%M')
            if current_time == alarm_time:
                speak("It's time!")
                break
            time.sleep(30)

    # Check every 30 seconds
    thread = threading.Thread(target=alarm_thread)
    thread.start()

# Check if the query is a math question
def is_math_question(query):
    """Check if the query is a math question."""
    math_keywords = ["calculate", "solve", "what is", "what's", "equals", "plus", "minus", "times", "divided by"]
    return any(keyword in query.lower() for keyword in math_keywords)

# Check if the query is a weather question
def is_weather_question(query):
    """Check if the query is a weather question."""
    weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"]
    return any(keyword in query.lower() for keyword in weather_keywords)

# Function to fetch weather information for a given city
def get_weather(city):
    """Fetch weather information for a given city."""
    api_key = 'YOURAPI'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is currently {weather_description} with a temperature of {temperature}°C."
    else:
        return "Sorry, I couldn't retrieve the weather information. Please check the city name or try again later."

# Function to search and provide an answer using Gemini API or another search API for general questions
def search_and_provide_answer(query):
    """Search and provide an answer using Gemini API or another search API for general questions."""
    try:
        if is_math_question(query):
            answer = solve_math_question(query)
            if answer is not None:
                speak(f"The answer is {answer}")
                print(f"The answer is {answer}")
            else:
                speak("Sorry, I couldn't calculate that. Please rephrase your question.")
        elif is_weather_question(query):
            # Extract the city from the query. This can be improved with a more sophisticated NLP approach.
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["in", "at", "for"]:
                    city = " ".join(words[i+1:])
                    break
            else:
                city = words[-1]
            weather_info = get_weather(city)
            speak(weather_info)
        else:
            # Use Gemini API or another search API for general questions
            response = chat.send_message(query)
            answer = response.text.strip()
            if answer:
                speak(answer)
            else:
                speak("I couldn't find relevant information. Could you please provide more details?")
    except Exception as e:
        speak(f"An error occurred while processing your request. Error: {e}")

# This gives some functionality to Nira for better responses
def classify_sentence(sentence):
    """Classify a sentence as a question or a statement."""
    words = word_tokenize(sentence)
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stopwords.words('english')]
    pos_tags = nltk.pos_tag(words)
    nouns = [word for word, pos in pos_tags if pos.startswith('N')]
    verbs = [word for word, pos in pos_tags if pos.startswith('V')]
    if len(nouns) > len(verbs):
        return "question"
    else:
        return "statement"

def show_notification(title, message):
    """Show a notification with the given title and message."""
    notification.notify(title=title, message=message, timeout=10)  # Notification duration in seconds (placeHolder)

async def bluetooth_scan():
    """Scan for Bluetooth devices and show a notification if a specific device is detected."""
    try:
        devices = await BleakScanner.discover()
        if devices:
            for device in devices:
                device_name = device.name if device.name else "Unknown Device"
                print(f"Bluetooth Device Found: {device.address} - {device_name}")
                # Adjust detection based on behavior or expected characteristics
                if "NothingPhone" in device.name:
                    show_notification("Bluetooth Device Detected", f"You passed by a {device.name} user!")
                    # Example: Use BleakClient to retrieve services and characteristics
                    try:
                        async with BleakClient(device) as client:
                            services = await client.get_services()
                            print(f"Services: {services}")
                            for service in services:
                                # Add logic to check for specific services or characteristics
                                pass
                    except Exception as e:
                        print(f"Error accessing services for {device.address}: {e}")
        else:
            print("No Bluetooth devices found.")
    except TypeError as e:
        print(f"Error discovering Bluetooth devices: {e}")

def nfc_detect(tag):
    """Detect NFC tags and show a notification if a specific tag is detected."""
    tag_id = tag.identifier.hex().upper()
    print(f"NFC Tag Detected: {tag_id}")
    # For debugging
    if tag_id == 'A14C1':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 1 user!")
    elif tag_id == 'A14C2':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2 user!")
    elif tag_id == 'A14C3':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2A user!")

async def run_nfc_scan():
    """Run NFC scan and connect to the NFC reader."""
    try:
        # Attempt to connect using different device paths
        clf = None
        possible_paths = ['usb', 'tty:S0', 'spi:']
        for path in possible_paths:
            try:
                clf = nfc.ContactlessFrontend(path)
                if clf:
                    break
            except IOError:
                continue
        if clf:
            clf.connect(rdwr={'on-connect': nfc_detect})
            clf.close()
        else:
            print("No NFC device found. Ensure your NFC reader is properly connected and recognized by your system.")
    except IOError as e:
        print(f"IOError: {e}")
    print("Ensure that the NFC reader is properly connected and recognized by your system.")

async def main():
    """Run NFC scan in the background and Bluetooth scan concurrently."""
    # Run NFC scan in the background
    nfc_task = asyncio.create_task(run_nfc_scan())
    # Run Bluetooth scan concurrently
    await bluetooth_scan()
    # Wait for NFC scan to complete
    await nfc_task

# Initialize the News client
def fetch_news(category):
    """Fetch news headlines for a given category."""
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey=YOUAPI"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles'][:5]  # Limiting to 5 articles for brevity
    return articles

# Lyric finder
def search_lyrics(song_title, musixmatch_api_key):
    """Search for song lyrics using the Musixmatch API."""
    base_url = "https://api.musixmatch.com/ws/1.1"
    headers = {"Authorization": f"Bearer {musixmatch_api_key}"}
    try:
        # Search for the song
        search_url = f"{base_url}/track.search"
        params = {"q_track": song_title, "page_size": 1, "apikey": musixmatch_api_key}
        search_response = requests.get(search_url, headers=headers, params=params)
        if search_response.status_code == 403:
            return "Forbidden: Check if your Musixmatch API key is correct and has proper permissions."
        if search_response.ok:
            search_results = search_response.json()
            tracks = search_results.get("message", {}).get("body", {}).get("track_list", [])
            if tracks:
                # Get the first result track
                track = tracks[0]["track"]
                track_id = track["track_id"]
                # Fetch song lyrics
                lyrics_url = f"{base_url}/track.lyrics.get"
                lyrics_params = {"track_id": track_id, "apikey": musixmatch_api_key}
                lyrics_response = requests.get(lyrics_url, headers=headers, params=lyrics_params)
                if lyrics_response.ok:
                    lyrics_data = lyrics_response.json()
                    lyrics = lyrics_data.get("message", {}).get("body", {}).get("lyrics", {}).get("lyrics_body", "Lyrics not found.")
                    return lyrics
                else:
                    return f"Failed to fetch lyrics. Status code: {lyrics_response.status_code}"
            else:
                return "Song not found in search results."
        else:
            return f"Failed to search for lyrics. Status code: {search_response.status_code} - {search_response.text}"
    except Exception as e:
        return f"An error occurred: {e}"

def get_youtube_summary(video_url):
    """Summarize a YouTube video using yt-dlp and a summarization model."""
    try:
        # Fetch video info using yt-dlp
        ydl_opts = {'quiet': True, 'skip_download': True, 'writeinfojson': True}
        # Extract video info with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        # Get video description or transcript
        transcript = info_dict.get('description', 'No transcript available.')
        # Use a summarization model
        summarizer = pipeline("summarization")
        summary = summarizer(transcript, max_length=150, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"An error occurred while processing your request. Error: {e}"

def search_and_provide_answer(query):
    """Search and provide an answer based on the command."""
    try:
        if is_weather_question(query):
            # Extract the city from the query.
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() in ["in", "at", "for"]:
                    city = " ".join(words[i+1:])
                    break
            else:
                city = words[-1]
            weather_info = get_weather(city)
            speak(weather_info)
        else:
            # Use an AI or search API for general questions
            response = chat.send_message(query)
            answer = response.text.strip()
            if answer:
                speak(answer)
            else:
                speak("I couldn't find relevant information. Could you please provide more details?")
    except Exception as e:
        speak(f"An error occurred while processing your request. Error: {e}")

# This gives some functionality to Nira for better responses
def classify_sentence(sentence):
    """Classify a sentence as a question or a statement."""
    words = word_tokenize(sentence)
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stopwords.words('english')]
    pos_tags = nltk.pos_tag(words)
    nouns = [word for word, pos in pos_tags if pos.startswith('N')]
    verbs = [word for word, pos in pos_tags if pos.startswith('V')]
    if len(nouns) > len(verbs):
        return "question"
    else:
        return "statement"

def show_notification(title, message):
    """Show a notification with the given title and message."""
    notification.notify(title=title, message=message, timeout=10)  # Notification duration in seconds (placeHolder)

async def bluetooth_scan():
    """Scan for Bluetooth devices and show a notification if a specific device is detected."""
    try:
        devices = await BleakScanner.discover()
        if devices:
            for device in devices:
                device_name = device.name if device.name else "Unknown Device"
                print(f"Bluetooth Device Found: {device.address} - {device_name}")
                # Adjust detection based on behavior or expected characteristics
                if "NothingPhone" in device.name:
                    show_notification("Bluetooth Device Detected", f"You passed by a {device.name} user!")
                    # Example: Use BleakClient to retrieve services and characteristics
                    try:
                        async with BleakClient(device) as client:
                            services = await client.get_services()
                            print(f"Services: {services}")
                            for service in services:
                                # Add logic to check for specific services or characteristics
                                pass
                    except Exception as e:
                        print(f"Error accessing services for {device.address}: {e}")
        else:
            print("No Bluetooth devices found.")
    except TypeError as e:
        print(f"Error discovering Bluetooth devices: {e}")

def nfc_detect(tag):
    """Detect NFC tags and show a notification if a specific tag is detected."""
    tag_id = tag.identifier.hex().upper()
    print(f"NFC Tag Detected: {tag_id}")
    # For debugging
    if tag_id == 'A14C1':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 1 user!")
    elif tag_id == 'A14C2':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2 user!")
    elif tag_id == 'A14C3':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2A user!")

async def run_nfc_scan():
    """Run NFC scan and connect to the NFC reader."""
    try:
        # Attempt to connect using different device paths
        clf = None
        possible_paths = ['usb', 'tty:S0', 'spi:']
        for path in possible_paths:
            try:
                clf = nfc.ContactlessFrontend(path)
                if clf:
                    break
            except IOError:
                continue
        if clf:
            clf.connect(rdwr={'on-connect': nfc_detect})
            clf.close()
        else:
            print("No NFC device found. Ensure your NFC reader is properly connected and recognized by your system.")
    except IOError as e:
        print(f"IOError: {e}")
    print("Ensure that the NFC reader is properly connected and recognized by your system.")

async def main():
    """Run NFC scan in the background and Bluetooth scan concurrently."""
    # Run NFC scan in the background
    nfc_task = asyncio.create_task(run_nfc_scan())
    # Run Bluetooth scan concurrently
    await bluetooth_scan()
    # Wait for NFC scan to complete
    await nfc_task

# Initialize the News client
def fetch_news(category):
    """Fetch news headlines for a given category."""
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey=fab33d4d84394644a2e2ddb4d372ffcd"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles'][:5]  # Limiting to 5 articles for brevity
    return articles

# Function to search and provide an answer based on the command
def parse_and_execute_command(command):
    """Parse and execute the user's command."""
    command = command.lower()
    musixmatch_api_key = "50e1bf84263cd5402215c3b0f01c04a1"
    classification = classify_sentence(command)

    # Convo
    if "who are you" in command:
        speak("I'm Nira, Your Personal AI assistant")
        return

    if any(greeting in command for greeting in greetings):
        search_and_provide_answer(command)
        return

    if any(compliment in command for compliment in compliments):
        speak(random.choice(responses_compliments))
        return

    if any(thank in command for thank in thanks):
        speak(random.choice(thank_responses))
        return

    if any(farewell in command for farewell in farewells):
        speak(random.choice(farewell_responses))
        exit()

    if any(wellbeing in command for wellbeing in wellbeing_inquiries):
        speak(random.choice(wellbeing_responses))
        return

    if any(hate in command for hate in hate_comments):
        speak(random.choice(responses_negative))
        return

    # Main commands
    if "lyrics" in command:
        song_name = command.lower().replace("lyrics", "").strip()
        lyrics = search_lyrics(song_name, musixmatch_api_key)
        speak(f"Lyrics for '{song_name}':\n{lyrics}")
        return

    if "imagerecognition" in command:
        perform_image_recognition()
    elif "full form of nira" in command:
        speak("Neural Advanced Interactive Network Assistant")
        return
    elif "help" in command:
        speak("The more information you give me, the better I can understand your needs and provide useful help. Please tell me more! I need more information to be helpful")
        return
    elif "what do you see" in command or "what is this" in command:
        answer_related_question(command)

    if random.random() < 0.01:
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley")

    if 'news' in command:
        if 'tech' in command:
            articles = fetch_news('technology')
            for article in articles:
                speak(f"{article['title']}: {article['url']}")
        elif 'sports' in command:
            articles = fetch_news('sports')
            for article in articles:
                speak(f"{article['title']}: {article['url']}")
        elif 'business' in command:
            articles = fetch_news('business')
            for article in articles:
                speak(f"{article['title']}: {article['url']}")
        elif 'entertainment' in command:
            articles = fetch_news('entertainment')
            for article in articles:
                speak(f"{article['title']}: {article['url']}")
        else:
            speak("Please specify a valid news category like tech, sports, business, or entertainment.")
    elif "repeat after me" in command:
        to_repeat = command.replace("repeat after me", "").strip()
        speak(to_repeat)
    elif "scan devices" in command:
        asyncio.run(main())
    elif "what is your name" in command or "who are you" in command:
        speak(f"I am {assistant_name}, Your assistant")
    elif "calculate" in command:
        try:
            expression = command.split("calculate")[1].strip()
            result = eval(expression)
            speak(f"The result of {expression} is {result}")
        except Exception as e:
            speak(f"Sorry, I couldn't calculate that. Error: {e}")
        return
    elif "who is your creator" in command:
        speak(f"I'm created by {creator_name}")
    elif "who created you" in command:
        speak(f"I'm created by {creator_name}")
    elif "who made you" in command:
        speak(f"I'm created by {creator_name}")
    elif "flip a coin" in command:
        result = flip_coin()
        speak(f"The result is: {result}")
    elif "tell me a joke" in command or "joke" in command:
        joke = fetch_joke()
        speak(joke)
    elif "remember" in command:
        tokens = command.split("remember")
        if len(tokens) > 1:
            info = tokens[1].strip()
            with open('memory.txt', 'a') as file:
                file.write(info + '\n')
            speak(f"I will remember that {info}")
    elif "forget" in command:
        tokens = command.split("forget")
        if len(tokens) > 1:
            info_to_forget = tokens[1].strip()
            forget_from_memory(info_to_forget)
    elif "play" in command and "song" in command:
        play_song(command)
    elif "what's the weather like in" in command or "weather in" in command:
        city_name = command.split("in")[-1].strip()
        weather_info = get_weather(city_name)
        speak(weather_info)
    elif "set timer for" in command:
        try:
            duration = int(command.split("for")[-1].strip().split()[0])
            set_timer(duration)
            speak(f"Timer set for {duration} seconds.")
        except ValueError:
            speak("Sorry, I couldn't understand the duration.")
    elif "set alarm for" in command:
        try:
            alarm_time = command.split("for")[-1].strip()
            set_alarm(alarm_time)
            speak(f"Alarm set for {alarm_time}.")
        except Exception as e:
            speak(f"Sorry, I couldn't set the alarm. Error: {e}")
    elif "tell me about" in command:
        topic = command.split("about")[-1].strip()
        search_and_provide_answer(f"What is {topic}")
    elif "bruh" in command:
        speak("Did I do something wrong or what?")
    elif "search" in command or "lookup" in command:
        search_term = command.replace("search", "").replace("lookup", "").strip()
        search_and_provide_answer(search_term)
    elif 'time' in command:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")
    elif 'python help' in command:
        provide_python_help(command.replace('python help', '').strip())
    elif 'play rock paper scissors' in command:
        play_game_rock_paper_scissors()
    elif classification == "question":
        search_and_provide_answer(command)
        return
    elif "summarize video" in command:
        video_url = command.split("summarize video")[-1].strip()
        summary = summarize_youtube_video(video_url)
        speak(summary)
    else:
        search_and_provide_answer(command)

    # After answering, wait for the next command

# Function to classify user input sentence
def classify_sentence(sentence):
    """Classify a sentence as a question or a statement."""
    words = word_tokenize(sentence)
    words = [word.lower() for word in words if word.isalnum() and word.lower() not in stopwords.words('english')]
    pos_tags = nltk.pos_tag(words)
    nouns = [word for word, pos in pos_tags if pos.startswith('N')]
    verbs = [word for word, pos in pos_tags if pos.startswith('V')]
    if len(nouns) > len(verbs):
        return "question"
    else:
        return "statement"

# Function to forget specific information from memory
def forget_from_memory(info_to_forget):
    """Forget specific information from memory."""
    try:
        with open('memory.txt', 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if info_to_forget not in line.strip():
                    file.write(line)
            file.truncate()
        speak(f"I have forgotten {info_to_forget}.")
    except Exception as e:
        speak(f"Sorry, I couldn't forget that. Error: {e}")

# Function to play a song using Spotify
def play_song(command):
    """Play a song using Spotify."""
    try:
        song_name = command.split("play")[-1].strip()
        results = sp.search(q=song_name, limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.start_playback(uris=[track_uri])
            speak(f"Playing {song_name} on Spotify.")
        else:
            speak(f"Sorry, I couldn't find {song_name} on Spotify.")
    except Exception as e:
        speak(f"Sorry, I couldn't play that song. Error: {e}")

# Function to translate text using Google Translate API
def translate_text(text, target_language='en'):
    """Translate text using Google Translate API."""
    try:
        response = requests.get(f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_language}&dt=t&q={text}")
        if response.status_code == 200:
            translation = response.json()[0][0][0]
            return translation
        else:
            return "Translation failed."
    except Exception as e:
        return f"Translation failed. Error: {e}"

# Function to fetch news headlines
def get_news_headlines():
    """Fetch news headlines."""
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {"country": "us", "apiKey": "fab33d4d84394644a2e2ddb4d372ffcd"}  # Replace with your NewsAPI key
        response = requests.get(url, params=params)
        if response.status_code == 200:
            news_data = response.json()
            headlines = [article['title'] for article in news_data['articles'][:5]]
            return headlines
        else:
            return []
    except Exception as e:
        return []

# Function to analyze sentiment of text using a pretrained model
def analyze_sentiment(text):
    """Analyze sentiment of text using a pretrained model."""
    try:
        # Use your NLP model for sentiment analysis
        return "Positive"  # Replace with actual sentiment analysis logic
    except Exception as e:
        return "Error analyzing sentiment."

# Function to provide help related to Python programming
def provide_python_help(topic):
    """Provide help related to Python programming."""
    try:
        # Provide help related to Python programming
        speak(f"Here is some help regarding {topic}.")
        # Replace with actual help content
    except Exception as e:
        speak(f"Sorry, I couldn't provide help regarding {topic}. Error: {e}")

# Function to play a game of rock-paper-scissors
def play_game_rock_paper_scissors():
    """Play a game of rock-paper-scissors."""
    try:
        speak("Let's play rock-paper-scissors. What's your choice?")
        player_choice = listen()
        if player_choice:
            choices = ['rock', 'paper', 'scissors']
            computer_choice = random.choice(choices)
            speak(f"I chose {computer_choice}.")
            if player_choice == computer_choice:
                speak("It's a tie!")
            elif (player_choice == 'rock' and computer_choice == 'scissors') or \
                 (player_choice == 'paper' and computer_choice == 'rock') or \
                 (player_choice == 'scissors' and computer_choice == 'paper'):
                speak("You win!")
            else:
                speak("I win!")
    except Exception as e:
        speak("Sorry, I couldn't play rock-paper-scissors. Error: {e}")

# Function to provide a recommendation based on user input
def provide_recommendation(recommendation_type):
    """Provide a recommendation based on user input."""
    try:
        # Provide recommendation based on user input
        speak(f"Here is a recommendation for {recommendation_type}.")
        # Replace with actual recommendation logic
    except Exception as e:
        speak(f"Sorry, I couldn't provide a recommendation for {recommendation_type}. Error: {e}")

# For coin flips
def flip_coin():
    """Flip a coin and return the result."""
    result = random.choice(["Heads", "Tails"])
    return result

# Main function to run the assistant
def run_assistant():
    """Run the assistant."""
    input_method = ""
    while input_method not in ["text", "voice"]:
        input_method = input("Do you want to give commands via text or voice? (Enter 'text' or 'voice'): ").strip().lower()
        if input_method not in ["text", "voice"]:
            speak("Invalid input method. Please enter 'text' or 'voice'.")

    greet_user()

    while True:
        command = listen(input_method)
        if command:
            continue_running = parse_and_execute_command(command)
        else:
            speak("Please provide a valid command.")

def process_input(command):
    """Process user input and perform actions based on the command."""
    global engine  # Ensure engine is accessible globally
    if "shut up" in command.lower() or "stop talking" in command.lower():
        engine.stop()  # Stop speech output
    else:
        speak("I didn't understand that command.")

# Main function to choose input method
# Start the assistant
if __name__ == "__main__":
    run_assistant()
