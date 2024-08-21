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
import replicate
import time
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import random
import yt_dlp as youtube_dl
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
import pygame
import cv2
import tensorflow as tf
import numpy as np
import asyncio
from bs4 import BeautifulSoup
import re
from PIL import Image
import requests
from io import BytesIO
from newsapi import NewsApiClient  
import google.generativeai as genai
from transformers import LlamaTokenizer, LlamaForCausalLM, AutoTokenizer
import socket
import sentencepiece
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import InferenceClient


# Initialize the tokenizer and model for Llama
llama_tokenizer = LlamaTokenizer.from_pretrained('facebook/llama-7b', use_auth_token='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')
llama_model = LlamaForCausalLM.from_pretrained('facebook/llama-7b', use_auth_token='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')

#==API==#

# Install newsapi-python library
genai.configure(api_key='AIzaSyArqhk1Y1Wt0JGtwW2tg2VglBAdpYzgklE')
gemini_model_name = 'gemini-1.5-pro-latest'
chat = genai.GenerativeModel(gemini_model_name).start_chat()

# Eleven Labs TTS API setup
ELEVEN_LABS_API_KEY = 'sk_08b25e1c9a132d21055d5123fcaaab37a0702e022f51d95a'
ELEVEN_LABS_VOICE_ID = 'vGQNBgLaiM3EdZtxIiuY'
# Initialize weather API with your API key
owm = pyowm.OWM('5a16d7f729e69aced4b2d8745c1d6f6c')  # Replace with your OpenWeatherMap API key

musixmatch_api_key = "50e1bf84263cd5402215c3b0f01c04a1"
#creator / AI name
assistant_name = "Nira"
creator_name = "Blobby"

# Download NLTK resources if not already downloaded
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

# Initialize currency converter
currency_converter = CurrencyRates()
btc_converter = BtcConverter()

# Initialize PyDictionary
dictionary = PyDictionary()

# Initialize pygame mixer
pygame.mixer.init()

# Initialize the recognizer
recognizer = sr.Recognizer()


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

#Nothing Phone Detection System
class NLPModel:
    def __init__(self):
        self.model = make_pipeline(StandardScaler(), SVC())
        self.load_model()

    def load_model(self):
        try:
            self.model = joblib.load('nlp_model.pkl')
        except FileNotFoundError:
            # Handle the absence of the model file
            pass

    def predict_intent(self, text):
        return self.model.predict([text])[0]

nlp_model = NLPModel()
    
#Audio Skiping of symbols
def preprocess_text(text):
    # Remove specific symbols like "*", "**"
    text = re.sub(r'\*\*|\*', '', text)  # Remove '**' and '*'
    return text

#default output
def speak(text):
    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Example of setting properties (optional)
    # engine.setProperty('rate', 150)    # Speed of speech
    # engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

    # Print the text with the prefix
    print(f"Nira: {text}")

    try:
        # Speak the text
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error during speech synthesis: {e}")

    # Cleanup
    engine.stop()
    
    

def listen(input_method):
    if input_method == "text":
        return listen_text()
    elif input_method == "voice":
        return listen_voice()
    else:
        speak("Invalid input method selected.")
        return None

def listen_text():
    command = input("Enter your command: ")
    print(f"You said: {command}")
    return command

def listen_voice():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio, show_all=False)
            if command:
                command = preprocess_text(command)
                print(f"You said: {command}")
                return command
            else:
                return None
    except sr.UnknownValueError:
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

#Identifies Maths Problems
def is_math_question(query):
    # Simple check to identify if the query is math-related
    math_keywords = ["calculate", "solve", "what is", "what's", "equals", "plus", "minus", "times", "divided by"]
    return any(keyword in query.lower() for keyword in math_keywords)

#Weather System
def get_weather(city):
    api_key = '5a16d7f729e69aced4b2d8745c1d6f6c'
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city} is currently {weather_description} with a temperature of {temperature}°C."
    else:
        return "Sorry, I couldn't retrieve the weather information. Please check the city name or try again later."

#gives temp Info for specific query
def is_weather_question(query):
    weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"]
    return any(keyword in query.lower() for keyword in weather_keywords)

# Function to check internet availability
def is_internet_available():
    try:
        requests.get('http://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Function to handle online and offline responses
def search_and_provide_answer(query):
    if is_math_question(query):
        try:
            # Safe evaluation for basic math questions
            result = eval(query, {"__builtins__": None}, {})
            answer = f"The answer to your question is {result}."
        except Exception as e:
            answer = f"Sorry, I couldn't calculate that. Error: {e}"
    elif is_weather_question(query):
        city = query.split()[-1]  # Extract city from query
        answer = get_weather(city)
    else:
        if is_internet_available():
            try:
                # Replace this with actual call to your online chat model
                # Example: response = chat.chat(query)  
                # Here, simulate response for demonstration
                response = {'text': "This is a simulated response from the Gemini model."}
                answer = response['text']
            except Exception as e:
                answer = f"Error using Gemini model: {e}"
        else:
            try:
                # Tokenize and generate response using Llama model
                inputs = llama_tokenizer(query, return_tensors="pt")
                with torch.no_grad():
                    outputs = llama_model.generate(**inputs, max_length=50)
                answer = llama_tokenizer.decode(outputs[0], skip_special_tokens=True)
            except Exception as e:
                answer = f"Error using Llama model: {e}"
    return answer


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

#notification funtion
def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10  # Notification duration in seconds(place Holder)
    )

#bluetooth scan
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

#NFC scan
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
def parse_and_execute_command(command):
    command = command.lower()
    classification = classify_sentence(command)
    now = datetime.datetime.now()
#convo 
    if command.startswith("generate image"):
        prompt = command[len("generate image "):]
        image_path = generate_image(prompt)
        if image_path:
            # Show the image or return a path, depending on your implementation
            return f"Image generated and saved as {image_path}."
        else:
            return "Failed to generate image."
    if 'who are you' in command.lower() or 'what is your name' in command.lower():
        responses = [
            f"Hello! I am {assistant_name}, your advanced AI assistant. My purpose is to help you with a variety of tasks, from answering questions to managing your schedule. I was created by {creator_name}, and I'm here to make your life easier and more enjoyable.",
            f"I'm {assistant_name}, your personal assistant designed to assist with a range of tasks. Created by {creator_name}, I'm here to make your day a bit easier and more efficient.",
            f"Hi there! I'm {assistant_name}, and I was built by {creator_name}. I'm here to help you with whatever you need, from answering your questions to managing your daily tasks.",
            f"Greetings! I am {assistant_name}, an AI assistant created by {creator_name}. My goal is to assist you in various tasks and provide you with useful information.",
            f"Hey! I'm {assistant_name}, your AI assistant. Designed by {creator_name}, I'm here to help you with a wide range of activities and make your life simpler."
        ]
        response = random.choice(responses)
        speak(response)
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

    elif "full form of nira" in command:
        speak("Neural Advanced Interactive Network Assistant")
        return
         
    elif "help" in command :
        speak("The more information you give me, the better I can understand your needs and provide useful help. Please tell me more! I need more information to be helpful")
        return
        
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
        
    elif 'bruh' in command.lower():
        responses = [
            "Oops! Did I mess up? Let me know how I can improve.",
            "Bruh! That was unexpected. How can I make it better?",
            "Looks like I might have made a mistake. Any suggestions?",
            "Well, that’s awkward. How can I assist you better?",
            "I guess I goofed up. What should I do differently?"
        ]
        response = random.choice(responses)
        speak(response)
        return
        
    elif "search" in command or "look up" in command:
        search_term = command.replace("search", "").replace("look up", "").strip()
        search_and_provide_answer(search_term)
        
    elif 'time' in command:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {strTime}")
        return
    
    elif 'day' in command:
        strDay = now.strftime("%A")
        speak(f"The day is {strDay}")
        return
        
    elif 'date' in command:
        strDate = now.strftime("%Y-%m-%d")
        speak(f"The date is {strDate}")
        return
    
    elif 'month' in command:
        strMonth = now.strftime("%B")
        speak(f"The month is {strMonth}")
        return
        
    elif 'year' in command:
        strYear = now.strftime("%Y")
        speak(f"The year is {strYear}")
        return
    
        
    elif 'python help' in command:
        provide_python_help(command.replace('python help', '').strip())
        
    elif 'play rock paper scissors' in command:
        play_game_rock_paper_scissors()
        
    elif classification == "question":
        search_and_provide_answer(command)
        return

        
    else:
        search_and_provide_answer(command)

    # After answering, wait for the next command


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
        
#game for RPS        

def play_game_rock_paper_scissors(input_method="text"):
    try:
        # Ask the player for their choice
        speak("Let's play rock-paper-scissors. What's your choice?")
        player_choice = listen(input_method).strip().lower()

        # Define valid choices
        choices = ['rock', 'paper', 'scissors']

        # Validate player's choice
        if player_choice not in choices:
            speak("Invalid choice. Please choose rock, paper, or scissors.")
            return

        # Computer makes a choice
        computer_choice = random.choice(choices)
        speak(f"I chose {computer_choice}.")

        # Determine the winner
        if player_choice == computer_choice:
            speak("It's a tie!")
        elif (player_choice == 'rock' and computer_choice == 'scissors') or \
             (player_choice == 'paper' and computer_choice == 'rock') or \
             (player_choice == 'scissors' and computer_choice == 'paper'):
            speak("You win!")
        else:
            speak("I win!")

    except Exception as e:
        # Handle any errors that occur
        speak(f"Sorry, I couldn't play rock-paper-scissors. Error: {e}")
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
            # If no command is received, you may choose to exit or retry
            speak("No command received. Please try again.")
            
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

