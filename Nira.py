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
import openai
# Ensure you have StableLM installed
from newsapi import NewsApiClient  
# Install newsapi-python library

openai.api_key = 'This is for a test purpose'

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
owm = pyowm.OWM('add your own')  # Replace with your OpenWeatherMap API key

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
        # Set up Google Custom Search API
        api_key = "ADD YOUR API"  # Replace with your API key
        search_engine_id = "Add your API"  # Replace with your search engine ID
        search_url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"

        # Make request to the API
        response = requests.get(search_url)
        data = response.json()

        # Parse the response
        if "items" in data:
            items = data["items"]
            if items:
                # Get the first relevant snippet
                snippet = items[0]["snippet"]
                speak(snippet)
            else:
                speak("No relevant information found.")
        else:
            speak("Error occurred while searching.")
    except Exception as e:
        speak(f"Error occurred while searching. Error: {e}")
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

def chatgpt_response(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Sorry, I couldn't process your request. Error: {e}"

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

    # Lists of phrases to match against
    compliments = ["you are beautiful", "you are smart", "you are awesome", "you're beautiful", "you're awesome", "you'er Kind", "you're sweet", "i love you", "i like you"]
    thanks = ["thanks", "thank you", "thank", "thank"]
    goodbye = ["goodbye", "bye", "exit"]
    classification = classify_sentence(command)
    if any(compliment in command for compliment in compliments):
        speak("Thank you!")
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
    elif "search" in command or "look up" in command:
        search_term = command.replace("search", "").replace("look up", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
    elif "object recognition" in command:
        speak("Please show me the object to recognize.")
        # Capture image using computer vision module and recognize
        # Replace with your computer vision logic
    elif "tell me about" in command:
        topic = command.split("about")[-1].strip()
        search_and_provide_answer(f"What is {topic}")
    elif "bruh" in command:
        speak("Did i do something wrong or what?")
    elif "open" in command:
        open_website(command)
    elif any(thank in command for thank in thanks):
        speak("You're welcome.")
    elif any(goodbye_command in command for goodbye_command in goodbye):
        speak("Goodbye! Have a great day. If you need anything else, feel free to reach out! im always here to Help! ")
        exit()
    elif classification == "question":
        search_and_provide_answer(command)
        return
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
