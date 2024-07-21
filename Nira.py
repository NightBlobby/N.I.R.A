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
# Install newsapi-python library

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
owm = pyowm.OWM('Your API')  # Replace with your OpenWeatherMap API key

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

# Initialize NLP model using sklearn (example setup)
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
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's command
def listen():
    try:
        while True:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")

            if "shut up" in command.lower() or "stop talking" in command.lower():
                engine.stop()
                break  # Exit the loop when command is detected
            else:
                parse_and_execute_command(command)

    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Could you repeat?")
        listen()  # Restart listening on unrecognized speech
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
    except Exception as e:
        speak(f"An error occurred: {e}")

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

# Function to send an email
def send_email():
    try:
        speak("Who is the recipient?")
        recipient = listen()
        speak("What is the subject?")
        subject = listen()
        speak("What is the message?")
        message_content = listen()

        msg = EmailMessage()
        msg.set_content(message_content)
        msg['Subject'] = subject
        msg['From'] = 'your_email@example.com'  # Replace with your email
        msg['To'] = recipient

        with smtplib.SMTP('smtp.example.com', 587) as server:  # Replace with your SMTP server and port
            server.starttls()
            server.login('your_email@example.com', 'your_password')  # Replace with your login credentials
            server.send_message(msg)

        speak("Email sent.")
    except Exception as e:
        speak(f"Could not send the email. Error: {e}")

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

def search_and_provide_answer(query):
    try:
        # Check if the query is a math question
        if is_math_question(query):
            answer = solve_math_question(query)
            if answer:
                speak(answer)
            else:
                speak("Sorry, I couldn't find an answer to that math question.")
        else:
            # Set up Google Custom Search API
            api_key = "your_api_key_here"  # Replace with your API key
            search_engine_id = "your_search_engine_id_here"  # Replace with your search engine ID
            search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"

            # Make request to the API
            response = requests.get(search_url)
            data = response.json()

            # Parse the response
            if "items" in data:
                items = data["items"]
                if items:
                    # Attempt to find the best answer
                    best_answer = find_best_answer(items)
                    if best_answer:
                        speak(best_answer)
                    else:
                        speak(items[0]["snippet"])  # Fallback to snippet if no structured answer found
                else:
                    speak("No relevant information found.")
            else:
                speak("Error occurred while searching.")
    except Exception as e:
        speak(f"Error occurred while searching. Error: {e}")

def is_math_question(query):
    # Function to check if the query is a math question
    # This is a simplified check, you may need to expand this depending on your use case
    math_keywords = ["solve", "math", "calculate", "what is", "how much"]
    for keyword in math_keywords:
        if keyword in query.lower():
            return True
    return False

def solve_math_question(query):
    # Function to solve the math question and return the answer
    # This is a simplified implementation, you may need to enhance this based on your requirements
    try:
        # Extract the math expression from the query
        math_expression = re.search(r'(?<=\bcalculate\b\s).*', query, re.IGNORECASE).group(0)
        
        # Evaluate the math expression
        answer = eval(math_expression)
        return f"The answer is {answer}"
    except Exception as e:
        print(f"Error solving math question: {e}")
        return None

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
# this gives some funtionality to chatgpt for better responses


def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Notification duration in seconds
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


# Function to search and provide an answer based on the command
# Function to parse and execute the user command
def parse_and_execute_command(command):
    command = command.lower()

    
    # Responses
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
        "Until next time!"
    ]

    greeting_responses = [
        "Hello!", "Hi there!", "Greetings!", "Hey!", "Good to see you!", "Hi!", "Hey there!"
    ]

    comforting_responses = [
        "I'm here for you.", "Everything will be alright.", "Don't worry, you're not alone.",
        "Take it easy, I'm listening.", "It's going to be fine.", "You can talk to me.",
        "I'm here to help.", "You can count on me."
    ]

    hate_responses = [
        "I'm sorry you feel that way. How can I help you?",
        "Let's try to work through this. What's bothering you?",
        "I'm here to assist you. What can I do to make things better?",
        "I understand. Let's talk about what's bothering you.",
        "I'm sorry if I've upset you. Please let me know how I can improve."
    ]

    sad_responses = [
        "I'm sorry that you're feeling this way. Remember, you're not alone.",
        "It's okay to feel this way. I'm here if you want to talk about it.",
        "I'm here to listen and support you. Take your time.",
        "I'm sorry you're going through this. Take a deep breath, I'm here for you.",
        "You're strong, and you can get through this. I'm here to help in any way I can.",
        "Remember that it's okay not to be okay sometimes. You can always talk to me."
    ]

    compliment_responses = [
        "Thank you! You're pretty awesome yourself!",
        "I appreciate that! You made my day!",
        "You're too kind! Thanks!",
        "Aw, shucks! Thanks for the compliment!"
    ]

    conversation_data = {
        "music": {
            "inputs": ["music", "favorite genre", "favorite band", "listen to music"],
            "responses": [
                "What's your favorite genre of music?",
                "I love listening to music. What about you?",
                "Music is such a great way to relax. Do you have a favorite band?"
            ]
        },
        "movies": {
            "inputs": ["movies", "favorite genre", "watch movies"],
            "responses": [
                "Do you enjoy watching movies? What's your favorite genre?",
                "I'm a fan of sci-fi movies. What about you?",
                "Have you seen any good movies lately?"
            ]
        },
        "books": {
            "inputs": ["books", "reading", "favorite book", "favorite genre"],
            "responses": [
                "Do you like reading? Any favorite books or genres?",
                "Books can be so inspiring. Have you read anything interesting recently?",
                "I enjoy reading mystery novels. What about you?"
            ]
        },
        "hobbies": {
            "inputs": ["hobbies", "fun activities", "what do you do for fun"],
            "responses": [
                "What do you like to do for fun?",
                "I like painting in my spare time. What about you?",
                "Hobbies are a great way to relax. Do you have any hobbies?"
            ]
        },
        "technology": {
            "inputs": ["technology", "latest gadget", "new apps or devices"],
            "responses": [
                "Are you interested in technology? What's the latest gadget you've come across?",
                "Technology is always evolving. Have you tried any new apps or devices?"
            ]
        },
        "travel": {
            "inputs": ["travel", "interesting trips", "favorite place to visit"],
            "responses": [
                "Have you been on any interesting trips lately?",
                "Traveling is so exciting. Where's the next place you want to visit?",
                "I love exploring new places. What about you?"
            ]
        },
        "food": {
            "inputs": ["food", "cooking", "favorite cuisine", "try new foods"],
            "responses": [
                "Do you enjoy cooking or trying new foods?",
                "Food is one of life's great pleasures. Any favorite cuisine?",
                "I love trying different foods. What's your favorite dish?"
            ]
        },
        "sports": {
            "inputs": ["sports", "favorite sport", "play any sports"],
            "responses": [
                "Are you a fan of any sports? Which ones do you enjoy?",
                "Sports can be so exciting to watch. Do you play any sports yourself?"
            ]
        },
        "pets": {
            "inputs": ["pets", "favorite animal", "have any pets"],
            "responses": [
                "Do you have any pets? What kind?",
                "Pets bring so much joy. Do you have a favorite animal?",
                "I love animals. Tell me about your pets."
            ]
        },
        "weather": {
            "inputs": ["weather", "sunny or rainy", "how's the weather"],
            "responses": [
                "How's the weather today where you are?",
                "The weather can really affect the day. Is it sunny or rainy there?"
            ]
        },
        "current_events": {
            "inputs": ["current events", "interesting news", "what's caught your attention"],
            "responses": [
                "Have you heard any interesting news lately?",
                "Keeping up with current events can be fascinating. What's caught your attention?"
            ]
        },
        "dreams": {
            "inputs": ["dreams", "recurring dreams", "dream interpretation"],
            "responses": [
                "Do you have any recurring dreams? What do you think they mean?",
                "Dreams can be so mysterious. Do you remember your dreams often?"
            ]
        },
        "goals": {
            "inputs": ["goals", "current goals", "big plans for the future"],
            "responses": [
                "What are some of your current goals?",
                "Setting goals can be motivating. Do you have any big plans for the future?"
            ]
        },
        "family": {
            "inputs": ["family", "tell me about your family", "close with them"],
            "responses": [
                "Tell me about your family. Are you close with them?",
                "Family is important. Do you have any siblings or relatives you're particularly close to?"
            ]
        },
        "work": {
            "inputs": ["work", "job", "rewarding part of your job"],
            "responses": [
                "What do you do for work? Do you enjoy it?",
                "Work can be challenging. What's the most rewarding part of your job?"
            ]
        },
        "school": {
            "inputs": ["school", "college", "studying", "favorite subjects"],
            "responses": [
                "Are you in school or college? What are you studying?",
                "Education opens up so many opportunities. What subjects do you enjoy?"
            ]
        },
        "memories": {
            "inputs": ["memories", "favorite memory", "special memory"],
            "responses": [
                "What's a favorite memory of yours?",
                "Memories shape who we are. Do you have a special memory that stands out to you?"
            ]
        },
        "art": {
            "inputs": ["art", "favorite style", "favorite artist", "artistic"],
            "responses": [
                "Do you appreciate art? What's your favorite style or artist?",
                "Art can be so inspiring. Do you have a favorite painting or sculpture?",
                "I find art fascinating. What's something artistic that you enjoy?"
            ]
        },
        "science": {
            "inputs": ["science", "scientific discoveries", "science topic"],
            "responses": [
                "Are you interested in science? What fields intrigue you?",
                "Science is constantly advancing. Have you read any interesting scientific discoveries lately?",
                "I'm curious about science. Is there a scientific concept or topic you find intriguing?"
            ]
        },
        "nature": {
            "inputs": ["nature", "outdoor activity", "favorite place in nature"],
            "responses": [
                "Do you love being in nature? What's your favorite outdoor activity?",
                "Nature is so beautiful. Do you have a favorite place in nature that you like to visit?",
                "I enjoy spending time outdoors. What about you?"
            ]
        },
        "history": {
            "inputs": ["history", "historical figure", "historical event"],
            "responses": [
                "Are you into history? What time period or historical figure do you find intriguing?",
                "History is full of fascinating stories. Is there a historical event or era you're curious about?",
                "I find history intriguing. What historical topics or figures interest you?"
            ]
        },
        "philosophy": {
            "inputs": ["philosophy", "philosophical question", "philosophical concept"],
            "responses": [
                "Do you enjoy philosophical discussions? What's a philosophical question you've pondered?",
                "Philosophy explores deep questions about life and existence. Is there a philosophical concept that intrigues you?",
                "I find philosophy thought-provoking. Do you have a favorite philosopher or idea?"
            ]
        },
        "fashion": {
            "inputs": ["fashion", "favorite style", "fashion icon"],
            "responses": [
                "What's your go-to style?",
                "Fashion trends are always changing. Is there a fashion icon you admire?",
                "Do you have a favorite piece of clothing or accessory?"
            ]
        },
        "finance": {
            "inputs": ["finance", "managing money", "financial goal"],
            "responses": [
                "Do you follow finance news? What's your approach to managing money?",
                "Finance plays a big role in our lives. What's your financial goal?",
                "Have you ever invested in stocks or cryptocurrencies?"
            ]
        },
        "cooking": {
            "inputs": ["cooking", "signature dish", "cuisine to master"],
            "responses": [
                "Do you enjoy cooking? What's your signature dish?",
                "Cooking can be so rewarding. Is there a cuisine you'd like to master?",
                "What's the last dish you cooked?"
            ]
        },
        "health": {
            "inputs": ["health", "wellness", "healthy habit"],
            "responses": [
                "Do you prioritize health and wellness? How do you take care of yourself?",
                "Health is wealth. What's your favorite healthy habit?",
                "Have you tried any new health trends or practices?"
            ]
        },
        "artificial intelligence": {
            "inputs": ["artificial intelligence", "AI impact", "AI breakthroughs"],
            "responses": [
                "Are you curious about artificial intelligence? What's a question you have about AI?",
                "AI technology is transforming various industries. How do you think AI will impact the future?",
                "Have you heard about any recent AI breakthroughs?"
            ]
        },
        "entertainment": {
            "inputs": ["entertainment", "favorite form", "favorite TV show"],
            "responses": [
                "What's your favorite form of entertainment? Movies, books, music, or something else?",
                "Entertainment helps us unwind. What's something entertaining you've enjoyed recently?",
                "Do you have a favorite TV show or movie series?"
            ]
        },
        "social media": {
            "inputs": ["social media", "impact on lives", "favorite platform"],
            "responses": [
                "Do you use social media? How do you think it's changed our lives?",
                "Social media connects people globally. What's your favorite platform?",
                "How do you balance social media use with other activities?"
            ]
        },
        "education": {
            "inputs": ["education", "topic to learn", "lifelong learning"],
            "responses": [
                "Are you passionate about education? What's a topic you'd like to learn more about?",
                "Education opens doors to new opportunities. How do you approach lifelong learning?",
                "Have you ever taken an online course or attended a workshop?"
            ]
        },
        "environment": {
            "inputs": ["environment", "reduce carbon footprint", "sustainability"],
            "responses": [
                "Are you concerned about the environment? What steps do you take to reduce your carbon footprint?",
                "Environmental conservation is important for future generations. How do you contribute to sustainability?",
                "Have you participated in any environmental initiatives or movements?"
            ]
        },
        "technology": {
            "inputs": ["technology", "latest gadget", "new apps or devices"],
            "responses": [
                "Are you interested in technology? What's the latest gadget you've come across?",
                "Technology is always evolving. Have you tried any new apps or devices?"
            ]
        },
        "coding": {
            "inputs": ["coding", "programming languages", "favorite IDE"],
            "responses": [
                "Do you enjoy coding? What programming languages do you like?",
                "Coding is like solving puzzles. What's your favorite IDE or development environment?"
            ]
        },
        "space": {
            "inputs": ["space", "cosmos", "astronomy"],
            "responses": [
                "Are you fascinated by space? What aspect of astronomy interests you the most?",
                "Space exploration is incredible. Do you have a favorite celestial body or event?"
            ]
        },
        "robotics": {
            "inputs": ["robotics", "robots", "AI in robotics"],
            "responses": [
                "Are you interested in robotics? What do you think about AI in robotics?",
                "Robots are changing industries. What's a recent advancement in robotics that caught your attention?"
            ]
        },
        "philosophy": {
            "inputs": ["philosophy", "ethical dilemmas", "existentialism"],
            "responses": [
                "Do you enjoy philosophical discussions? What ethical dilemmas do you find intriguing?",
                "Existential questions can be thought-provoking. What's a philosophical concept you ponder?"
            ]
        },
        "languages": {
            "inputs": ["languages", "learning a new language", "favorite language"],
            "responses": [
                "Do you speak multiple languages or are you learning a new one?",
                "Learning languages opens doors to new cultures. What's your favorite language?"
            ]
        },
        "games": {
            "inputs": ["games", "video games", "board games"],
            "responses": [
                "Do you enjoy playing games? Video games or board games?",
                "Games are a great way to unwind. What's your favorite video game or board game?"
            ]
        }
        # Add more topics and responses as desired
    }

    classification = classify_sentence(command)
    if "image recognition" in command:
        perform_image_recognition()
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
        speak(f"im created by {creator_name}")
    elif "who created you" in command:
        speak(f"im created by {creator_name}")
    elif "who made you" in command:
        speak(f"im created by {creator_name}")
    elif "open youtube" in command:
        speak("Opening Youtube.")
        webbrowser.open("https://www.youtube.com")
    elif "open google" in command:
        speak("Opening Google.")
        webbrowser.open("https://www.google.com")
    elif "open spotify" in command:
        speak("Opening Spotify.")
        webbrowser.open("https://open.spotify.com")
    elif "open discord" in command:
        speak("Opening Discord.")
        webbrowser.open("https://discord.com")
    elif "open email" in command or "open gmail" in command:
        speak("Opening Email.")
        webbrowser.open("https://mail.google.com")
    elif "flip a coin" in command:
        result = flip_coin()
        speak(f"The result is: {result}")
    elif "open g drive" in command:
        speak("Opening Google Drive.")
        webbrowser.open("https://drive.google.com")
    elif "open calendar" in command:
        speak("Opening Calendar.")
        webbrowser.open("https://calendar.google.com")
    elif "tell me a joke" in command or "joke" in command:
        joke = fetch_joke()
        speak(joke)
    elif "what can you do" in command or "help" in command:
        speak("I can help you with tasks like sending emails, fetching weather, setting timers, alarms, and more. Just ask!")
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
    elif "send email" in command:
        send_email()
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
        speak("Did i do something wrong or what?")
    elif "open" in command:
        open_website(command)
    elif any(thank in command.lower() for thank in thanks):
     speak(random.choice(thank_responses))
    elif any(farewell in command.lower() for farewell in farewells):
     speak(random.choice(farewell_responses))
     exit()
    elif "open netflix" in command:
        speak("Opening Netflix.")
        webbrowser.open("https://www.netflix.com")
    elif "open prime video" in command or "open amazon prime video" in command:
        speak("Opening Amazon Prime Video.")
        webbrowser.open("https://www.primevideo.com")
    elif "open zoom" in command or "open zoom app" in command:
        speak("Opening Zoom.")
        webbrowser.open("https://zoom.us")
    elif "search" in command or "look up" in command:
        search_term = command.replace("search", "").replace("look up", "").strip()
        search_and_provide_answer(query)
    elif 'time' in statement:
            strTime=datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"the time is {strTime}")
    elif 'python help' in command:
        provide_python_help(command.replace('python help', '').strip())
    elif 'play rock paper scissors' in command:
        play_game_rock_paper_scissors()
    elif 'recommendation' in command:
        provide_recommendation(command.replace('recommendation', '').strip())
    elif classification == "question":
        search_and_provide_answer(command)
        return
    elif "help" in command or "what can you do" in command or "what are your capabilities" in command:
        speak("I can help you with various tasks like searching the web, opening applications, fetching news, and more. Just let me know what you need!")
    for topic, data in conversation_data.items():
        if any(input_word in command for input_word in data["inputs"]):
            return random.choice(data["responses"])

    if any(greeting_word in command for greeting_word in greeting_responses):
        return random.choice(greeting_responses)
    elif any(thank_word in command for thank_word in thank_responses):
        return random.choice(thank_responses)
    elif any(hate_word in command for hate_word in hate_responses):
        return random.choice(hate_responses)
    elif any(sad_word in command for sad_word in sad_responses):
        return random.choice(sad_responses)
    elif any(compliment_word in command for compliment_word in compliment_responses):
        return random.choice(compliment_responses)
    elif any(comfort_word in command for comfort_word in comforting_responses):
        return random.choice(comforting_responses)    
    else:
        speak("")
    

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
            "apiKey": "your_newsapi_key"  # Replace with your News API key
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
def flip_coin():
    result = random.choice(["Heads", "Tails"])
    return result
# Main function to run the assistant
def run_assistant():
    greet_user()
    while True:

        command = listen()
        if command:
            parse_and_execute_command(command)
        else:
            speak("")
def process_input(command):
    global engine  # Ensure engine is accessible globally
    if "shut up" in command.lower() or "stop talking" in command.lower():
        engine.stop()  # Stop speech output
    else:
        speak("I didn't understand that command.")
# Start the assistant
if __name__ == "__main__":
    run_assistant()
