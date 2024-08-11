#===========================================================================================================================================
##MIT License

#Copyright (c) 2024 NightBlobby

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


#============================================================================================================================================



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
# Ensure you have StableLM installed
from newsapi import NewsApiClient  
import google.generativeai as genai


# Install newsapi-python library
genai.configure(api_key='YOUR API')
model = genai.GenerativeModel('gemini-1.5-pro-latest')
chat = model.start_chat()

#creator / AI name

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
owm = pyowm.OWM('YOU API')  # Replace with your OpenWeatherMap API key

# Initialize Spotify API (Replace placeholders with your credentials)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_CLIENT_ID",
                                               client_secret="YOUR_CLIENT_SECRET",
                                               redirect_uri="YOUR_REDIRECT_URI",
                                               scope="user-read-playback-state,user-modify-playback-state"))

# Initialize PyDictionary
dictionary = PyDictionary()

# Function to greet the user based on the time of day
def greet_user():
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
    def __init__(self):
        self.model = make_pipeline(StandardScaler(), SVC())
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load('nlp_model.pkl')
        except FileNotFoundError:
            # Train or load your NLP model here
            pass

    def predict_intent(self, text):
        return self.model.predict([text])[0]

nlp_model = NLPModel()

# Function to speak
def speak(text):
    output = f"{assistant_name}: {text}"
    print(output)
    engine.say(text)
    engine.runAndWait()
    

# Function to listen to the user's command
def listen(input_method):
    if input_method == "text":
        return listen_text()
    elif input_method == "voice":
        return listen_voice()
    else:
        speak("Invalid input method selected.")
        return None

# Function to listen to the user's command via text input
def listen_text():
    command = input("Enter your command: ")
    print(f"You said: {command}")
    return command

# Function to listen to the user's command via voice input
def listen_voice():
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
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    if response.status_code == 200:
        joke_data = response.json()
        return f"{joke_data['setup']} ... {joke_data['punchline']}"
    else:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you get if you cross a cat with a dark horse? Kitty Perry.",
            "Why don't some couples go to the gym? Because some relationships don't work out.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised."
        ]
        return random.choice(jokes)


# Function to set a timer
def set_timer(duration_seconds):
    def timer_thread():
        time.sleep(duration_seconds)
        speak("Time's up!")
    thread = threading.Thread(target=timer_thread)
    thread.start()

# Function to set an alarm
def set_alarm(alarm_time):
    def alarm_thread():
        while True:
            current_time = datetime.datetime.now().strftime('%H:%M')
            if current_time == alarm_time:
                speak("It's time!")
                break
            time.sleep(30)  # Check every 30 seconds
    thread = threading.Thread(target=alarm_thread)
    thread.start()
# Function to search and provide an answer using Google Custom Search API

def is_math_question(query):
    # Simple check to identify if the query is math-related
    math_keywords = ["calculate", "solve", "what is", "what's", "equals", "plus", "minus", "times", "divided by"]
    return any(keyword in query.lower() for keyword in math_keywords)


def is_weather_question(query):
    weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"]
    return any(keyword in query.lower() for keyword in weather_keywords)

def get_weather(city):
    api_key = 'YOUR API'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is currently {weather_description} with a temperature of {temperature}°C."
    else:
        return "Sorry, I couldn't retrieve the weather information. Please check the city name or try again later."

def search_and_provide_answer(query):
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
                    
            else:
                city = words[-1]
                
            weather_info = get_weather(city)
            speak(weather_info)
 
        else:
            # Use Gemini API or another search API for general questions
            # Replace with actual API call and handle responses
            response = chat.send_message(query)
            answer = response.text.strip()

            if answer:
                speak(answer)
                print(answer)
            else:
                speak("I couldn't find relevant information. Could you please provide more details?")
                
    except Exception as e:
        speak(f"An error occurred while processing your request. Error: {e}")
        

# this gives some funtionality to Nira for better responses

def classify_sentence(sentence):
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
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Notification duration in seconds(place Holder)
    )

async def bluetooth_scan():
    try:
        devices = await BleakScanner.discover()
        if devices:
            for device in devices:
                device_name = device.name if device.name else "Unknown Device"
                print(f"Bluetooth Device Found: {device.address} - {device_name}")
                
                # Adjust detection based on behavior or expected characteristics
                if "Nothing Phone" in str(device.name):
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
    tag_id = tag.identifier.hex().upper()
    print(f"NFC Tag Detected: {tag_id}")  # For debugging
    if tag_id == 'A14C1':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 1 user!")
    elif tag_id == 'A14C2':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2 user!")
    elif tag_id == 'A14C3':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2A user!")

async def run_nfc_scan():
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
    # Run NFC scan in the background
    nfc_task = asyncio.create_task(run_nfc_scan())

    # Run Bluetooth scan concurrently
    await bluetooth_scan()

    # Wait for NFC scan to complete
    await nfc_task

# Initialize the News client
def fetch_news(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey=YOU API"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles'][:5]  # Limiting to 5 articles for brevity
    return articles

#Lyric finder

def search_lyrics(song_title, musixmatch_api_key):
    base_url = "https://api.musixmatch.com/ws/1.1"
    headers = {"Authorization": f"Bearer {musixmatch_api_key}"}

    try:
        # Search for the song
        search_url = f"{base_url}/track.search"
        params = {
            "q_track": song_title,
            "page_size": 1,
            "apikey": musixmatch_api_key
        }
        search_response = requests.get(search_url, headers=headers, params=params)
        
        if search_response.status_code == 403:
            return "Forbidden: Check if your Musixmatch API key is correct and has proper permissions."
        
        if search_response.ok:
            search_results = search_response.json()
            tracks = search_results.get("message", {}).get("body", {}).get("track_list", [])

            if tracks:
                # Get the first result
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
    try:
        # Fetch video info using yt-dlp
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'writeinfojson': True
        }
        
        # Extract video info
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
        

# this gives some funtionality to Nira for better responses

def classify_sentence(sentence):
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
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Notification duration in seconds(place Holder)
    )

async def bluetooth_scan():
    try:
        devices = await BleakScanner.discover()
        if devices:
            for device in devices:
                device_name = device.name if device.name else "Unknown Device"
                print(f"Bluetooth Device Found: {device.address} - {device_name}")
                
                # Adjust detection based on behavior or expected characteristics
                if "Nothing Phone" in str(device.name):
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
    tag_id = tag.identifier.hex().upper()
    print(f"NFC Tag Detected: {tag_id}")  # For debugging
    if tag_id == 'A14C1':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 1 user!")
    elif tag_id == 'A14C2':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2 user!")
    elif tag_id == 'A14C3':
        show_notification("NFC Tag Detected", "You passed by a Nothing Phone 2A user!")

async def run_nfc_scan():
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
    # Run NFC scan in the background
    nfc_task = asyncio.create_task(run_nfc_scan())

    # Run Bluetooth scan concurrently
    await bluetooth_scan()

    # Wait for NFC scan to complete
    await nfc_task

# Initialize the News client
def fetch_news(category):
    url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey=fab33d4d84394644a2e2ddb4d372ffcd"
    response = requests.get(url)
    news_data = response.json()
    articles = news_data['articles'][:5]  # Limiting to 5 articles for brevity
    return articles

# Responses and phrases
responses_compliments = [
    "Thank you!",
    "I appreciate it!",
    "You're so kind!",
    "That means a lot to me!",
    "Thanks a bunch!",
    "You're awesome!",
    "You're making me blush!",
    "You just made my day!",
    "That's so sweet of you!",
    "You really know how to make me smile!"
]

thank_responses = [
    "You're welcome!",
    "No problem!",
    "Anytime!",
    "My pleasure!",
    "Glad I could help!",
    "You're very welcome!"
]

farewell_responses = [
    "Goodbye!",
    "See you later!",
    "Take care!",
    "Farewell!",
    "Catch you later!",
    "Until next time!",
    "Bye for now!",
    "See you around!",
    "Have a great day!",
    "See you soon!",
    "Bye-bye!",
    "Take it easy!",
    "Have a good one!",
    "Until we meet again!"
]

compliments = [
    "you are beautiful", "you are smart", "you are awesome", "you're beautiful", 
    "you're awesome", "you're kind", "you're sweet", "i love you", "i like you",
    "you're amazing", "you're incredible", "you're fantastic", "you're wonderful",
    "you're brilliant", "you're the best", "you have a great sense of humor",
    "you are so talented", "you are so creative", "you're very thoughtful",
    "you're an inspiration", "you have a beautiful smile", "you have a great personality",
    "you're so charming", "you're so caring", "you're very generous", "you have a kind heart",
    "you're a great friend", "you're a true friend", "you're a wonderful person",
    "you make the world a better place", "you light up the room", "you're so strong",
    "you're so brave", "you're so positive", "you're so supportive", "you're very patient",
    "you are very understanding", "you have a beautiful soul", "you have a great energy",
    "you are very hardworking", "you are very dedicated", "you're so funny", 
    "you make me happy", "you make me laugh", "you always know what to say",
    "you have a great heart", "you're very humble", "you're very respectful",
    "you're a great listener", "you're very wise", "you're very knowledgeable",
    "you're so down-to-earth", "you're so easy to talk to", "you have a great voice",
    "you have a great laugh", "you are very interesting", "you are very engaging",
    "you are so reliable", "you are very trustworthy", "you're very honest",
    "you're very loyal", "you're very considerate", "you're very responsible",
    "you are very dependable", "you have a great outlook on life", "you are very positive",
    "you are very optimistic", "you are very motivating", "you are very inspiring",
    "you are very uplifting", "you are very encouraging", "you always make my day",
    "you always bring a smile to my face", "you have a great attitude", 
    "you have a great sense of style", "you are very passionate", "you are very enthusiastic",
    "you are very energetic", "you are very fun", "you are very lively",
    "you have a great spirit", "you have a great presence", "you are very charismatic",
    "you are very charming", "you are very captivating", "you have a magnetic personality"
]

thanks = [
    "thanks", "thank you", "thank", "thanks a lot", "thanks so much", "thank you very much",
    "thanks a bunch", "thanks a million", "thanks a ton", "thanks for everything",
    "thank you so much", "thank you very much", "thank you so very much", "many thanks",
    "thank you kindly", "much obliged", "thanks for your help", "thanks for your time",
    "thanks for the help", "thank you for your help", "thank you for your time",
    "thank you for the help", "thanks for your assistance", "thank you for your assistance",
    "thanks for assisting me", "thank you for assisting me", "thanks for your support",
    "thank you for your support", "thanks for supporting me", "thank you for supporting me"
]

farewells = [
    "goodbye", "bye", "exit", "see you", "see you later", "farewell", "take care",
    "catch you later", "later", "adios", "ciao", "au revoir", "so long", "see ya",
    "peace out", "i'm out", "talk to you later", "until next time", "until we meet again",
    "have a good day", "have a nice day", "have a great day", "see you soon",
    "bye-bye", "take it easy", "have a good one", "stay safe", "take care of yourself", "cya", "tata"
]

hate_comments = [
    "I don't like you",
    "You're annoying",
    "I hate you",
    "Go away",
    "I can't stand you",
    "Stop bothering me",
    "You're the worst",
    "I don't want to talk to you",
    "I dislike you",
    "Leave me alone"
]

responses_negative = [
    "I'm sorry you feel that way.",
    "I didn't mean to upset you.",
    "Let's try to stay positive.",
    "I'm here to help, not to cause frustration.",
    "If there's anything specific bothering you, let me know.",
    "I'm here to assist, not to cause any discomfort.",
    "I'm sorry if I did something wrong. How can I make it right?",
    "I hope we can resolve any issues you might have.",
    "I'm here to assist you. Let's work through this together.",
    "I'm here to help, so let me know how I can assist you better."
]

wellbeing_inquiries = [
    "how are you", "how are you doing", "how's it going", "how do you feel", 
    "how's everything", "how's life", "how's your day", "how are things", 
    "are you okay", "how have you been", "what's up", "how are you today",
    "how's your mood", "how are you holding up", "how's it been", 
    "how's your status", "how's your condition", "how do you feel today", "how you been",
    "how are you feeling", "what's new", "how's your energy", "how's it hanging",
    "how's your vibe", "how's your spirit", "how are you faring", "how do you do",
    "how are you holding on", "how's your mental state", "how's your wellbeing", 
    "how's everything going", "how's your health", "how's your day going", 
    "how's your system running", "what's your status", "what's your state", 
    "how's the system", "how's your functionality", "how's your performance",
    "how's your operating status", "how are you operating", "how are you functioning",
    "how are you managing", "how's your disposition", "how's your outlook", 
    "how are you feeling today", "how's your overall status", "how's your overall health"
]

wellbeing_responses = [
    "I'm doing well, thank you!", "I'm here to assist you!", "All systems are operational!", 
    "Feeling great and ready to help!", "I'm functioning at full capacity!", 
    "I'm just a bunch of code, but thanks for asking!", "Ready to assist you with anything you need!",
    "I'm doing fantastic, how can I help you today?", "I'm as good as a digital assistant can be!", 
    "Thank you for asking, I'm here to serve!", "I'm here and ready to assist!",
    "I'm operational and ready to assist you!", "I'm feeling great, thanks for asking!",
    "I'm at your service, what can I do for you today?", "Everything's running smoothly on my end!",
    "I'm feeling optimal today!", "I'm energized and ready to assist!", 
    "I'm in perfect working condition!", "All systems are go!", "I'm happy to help you today!",
    "I'm fully charged and ready to go!", "I'm feeling very productive!",
    "I'm always here to help you!", "I'm at peak performance!",
    "I'm functioning as expected!", "I'm ready to tackle any task you have for me!",
    "I'm feeling top-notch!", "I'm excited to assist you!", "Everything is working perfectly!",
    "I'm feeling excellent, thank you!", "I'm feeling fantastic today!",
    "I'm ready and operational!", "I'm feeling good, how can I help?", 
    "I'm doing well and ready to assist!", "I'm in great shape, thank you!",
    "I'm doing superb, how can I be of service?", "I'm feeling wonderful!",
    "I'm in excellent form today!", "I'm ready and waiting for your commands!",
    "I'm feeling quite well, thank you!", "Everything is running smoothly!",
    "I'm ready to help with anything you need!", "I'm functioning perfectly!",
    "I'm feeling better than ever!", "I'm all set to assist you!",
    "I'm in tip-top shape!", "I'm here and operational!"
]

greetings = [
    "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
    "greetings", "what's up", "howdy", "hey there", "hi there", "hiya",
    "morning", "afternoon", "evening", "what's good", "salutations",
    "hey buddy", "how's it going", "yo", "sup", "hey you", "hey pal",
    "howdy partner", "hello friend", "hey friend", "hi friend", 
    "good day", "top of the morning", "good to see you", "long time no see",
    "hey mate", "hello there", "hi everyone", "good to hear from you",
    "hi folks", "hello world", "hey gang", "g'day", "how's everything going",
    "hey there good lookin'", "hiya pal", "hello there buddy", "what's happening",
    "what's going on", "hey there champ", "hey there sport", "what's new"
]


# Function to search and provide an answer based on the command
def parse_and_execute_command(command):
    command = command.lower()
    musixmatch_api_key = "50e1bf84263cd5402215c3b0f01c04a1"
    classification = classify_sentence(command)
    
#convo 
    if "who are you" in command:
        speak("Im Nira, Your Personal AI assistant")
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

#main commands  
#   if "lyrics" in command:
#       song_name = command.lower().replace("lyrics", "").strip()
#        lyrics = search_lyrics(song_name, genius_token)
#        speak(f"Lyrics for '{song_name}':\n{lyrics}")
#        return

    if "image recognition" in command:
        perform_image_recognition()
    
    
    elif "full form of nira" in command:
        speak("Neural Advanced Interactive Network Assistant")
        return
         
    elif "help" in command :
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
        
    elif "search" in command or "look up" in command:
        search_term = command.replace("search", "").replace("look up", "").strip()
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
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "apiKey": "fab33d4d84394644a2e2ddb4d372ffcd"  # Replace with your News API key
        }
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
    try:
        # Use your NLP model for sentiment analysis
        return "Positive"  # Replace with actual sentiment analysis logic
    except Exception as e:
        return "Error analyzing sentiment."

# Function to provide help related to Python programming
def provide_python_help(topic):
    try:
        # Provide help related to Python programming
        speak(f"Here is some help regarding {topic}.")  # Replace with actual help content
    except Exception as e:
        speak(f"Sorry, I couldn't provide help regarding {topic}. Error: {e}")

# Function to play a game of rock-paper-scissors
def play_game_rock_paper_scissors():
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
    try:
        # Provide recommendation based on user input
        speak(f"Here is a recommendation for {recommendation_type}.")  # Replace with actual recommendation logic
    except Exception as e:
        speak(f"Sorry, I couldn't provide a recommendation for {recommendation_type}. Error: {e}")
      
#for coin flips   
        
def flip_coin():
    result = random.choice(["Heads", "Tails"])
    return result



# Main function to run the assistant

def run_assistant():
    
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
    global engine  # Ensure engine is accessible globally
    if "shut up" in command.lower() or "stop talking" in command.lower():
        engine.stop()  # Stop speech output
    else:
        speak("I didn't understand that command.")
# Main function to choose input method

# Start the assistant
if __name__ == "__main__":
    run_assistant()
