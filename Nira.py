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


import datetime
import webbrowser
import random
import requests
import asyncio
import re
import json
import os
import google.generativeai as genai
import re
from google.api_core.exceptions import InternalServerError

#==API==#
# Install newsapi-python library
genai.configure(api_key='YOUR API')
model = genai.GenerativeModel('gemini-1.5-pro-latest')
chat = model.start_chat()

#creator / AI name
assistant_name = "Nira"
creator_name = "Blobby"

# File to store questions and answers
qa_file = r'C:\Users\Admin\Desktop\AI\qa_data.json'

def load_qa_data():
    if os.path.exists(qa_file):
        with open(qa_file, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_qa_data(data):
    with open(qa_file, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize QA data
qa_data = load_qa_data()

def update_qa_data(question, answer):
    qa_data[question] = answer
    save_qa_data(qa_data)

def fetch_answer_from_ai(query):
    response = chat.send_message(query)
    return response.text.strip()

def search_and_provide_answer(query):
    global qa_data

    # Check if the query is in the stored data
    if query in qa_data:
        print(f"{qa_data[query]}")
        return
    else:
        # Fetch answer from AI
        answer = fetch_answer_from_ai(query)
        if answer:
            print(f"{answer}")
            # Store the answer for future reference
            update_qa_data(query, answer)
            return
        else:
            print("I couldn't find relevant information. Could you please provide more details?")

shortcut_mapping = {
    "u": "you",
    "r": "are",
    "pls": "please",
    "thx": "thanks",
    "ur": "you",  # Add this line
    "brb": "be right back",
    "btw": "by the way",
    "omg": "oh my god",
    "ttyl": "talk to you later",
    "idk": "I don't know",
    "bff": "best friends forever",
    "lol": "laugh out loud",
    "imo": "in my opinion",
    "tbh": "to be honest",
    "gm": "good morning",
    "gn": "good night",
    "gr8": "great",
    "asap": "as soon as possible",
    "cya": "see you",
    # Add more shortcuts as needed
}
def expand_shortcuts(sentence, mapping):
    for shortcut, full_form in mapping.items():
        sentence = re.sub(r'\b' + re.escape(shortcut) + r'\b', full_form, sentence, flags=re.IGNORECASE)
    return sentence

# Function to greet the user based on the time of day
def greet_user():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        print(f"Good morning! How can I assist you today?")
    elif 12 <= hour < 17:
        print(f"Good afternoon! How can I assist you today?")
    elif 17 <= hour < 20:
        print(f"Good evening! How can I assist you today?")
    else:
        print(f"Good night! How can I assist you today?")
    
    print(f"I am {assistant_name}, your personal assistant.")
    now = datetime.datetime.now()
    print(f"Today is {now.strftime('%A, %B %d, %Y')}, and the time is {now.strftime('%I:%M %p')}.")


# Function to fetch a joke from an online API
def fetch_joke():
    try:
        # Define the API endpoint for fetching jokes
        url = "https://v2.jokeapi.dev/joke/Any?type=single"  # Fetches a single joke of any type
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            joke_data = response.json()
            # Check if the joke is of type 'single' or 'twopart'
            if 'joke' in joke_data:
                return joke_data['joke']
            elif 'setup' in joke_data and 'delivery' in joke_data:
                return f"{joke_data['setup']} ... {joke_data['delivery']}"
        else:
            raise Exception("Failed to fetch joke from API")

    except Exception as e:
        print(f"Error: {e}")
        # Fallback jokes when fetching fails
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you get if you cross a cat with a dark horse? Kitty Perry.",
            "Why don't some couples go to the gym? Because some relationships don't work out.",
            "I told my wife she was drawing her eyebrows too high. She looked surprised."
        ]
        return random.choice(jokes)

def normalize_text(text):
    # Define common shortcuts and their full forms
    shortcuts = {
        "ur": "your",
        "u": "you",
        "r": "are",
        "idk": "I don't know",
        "btw": "by the way",
        "brb": "be right back",
        "ttyl": "talk to you later",
        "lol": "laugh out loud",
        "omg": "oh my god",
        "bff": "best friends forever",
        "thx": "thanks",
        "pls": "please",
        "gonna": "going to",
        "wanna": "want to",
        "cuz": "because",
        "gotta": "got to",
        "y": "why",
        "im": "I am",
        "ive": "I have",
        "dont": "don't",
        "doesnt": "doesn't",
        "cant": "can't",
        "wont": "won't",
        "shouldnt": "shouldn't",
        "wouldnt": "wouldn't",
        "couldnt": "couldn't",
        "wasnt": "wasn't",
        "werent": "weren't",
        "hasnt": "hasn't",
        "hadnt": "hadn't",
        "havent": "haven't",
        "mustnt": "mustn't",
        "mightnt": "mightn't",
        "neednt": "needn't",
        "shallnt": "shan't",
        "shant": "shan't",
        "willnt": "won't",
        "wouldnt": "wouldn't"
    }

    # Convert text to lowercase to ensure uniformity
    text = text.lower()

    # Replace shortcuts with their full forms
    for shortcut, full_form in shortcuts.items():
        text = text.replace(shortcut, full_form)
    
    return text


def preprocess_text(text):
    replacements = {
        "ur": "you're",
        "u": "you",
        "your": "you're",
        "u'r": "you're",
        "y'r": "you're",
        "u're": "you're",
        "u r": "you are",
        "you're": "you're",
        "you are": "you're",
    }
    
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text

# Path to the dictionary file
dictionary_file = r'C:\Users\Admin\Desktop\AI\dictionary.json'

def load_dictionary():
    if os.path.exists(dictionary_file):
        with open(dictionary_file, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_dictionary(dictionary):
    with open(dictionary_file, 'w') as file:
        json.dump(dictionary, file, indent=4)

def search_word_in_dictionary(word):
    dictionary = load_dictionary()
    return dictionary.get(word.lower(), None)

def update_dictionary(word, definition):
    dictionary = load_dictionary()
    dictionary[word.lower()] = definition
    save_dictionary(dictionary)
    
def classify_sentence(sentence):
    
    # Convert the sentence to lowercase for uniformity
    sentence = sentence.lower()

    # Wellbeing phrases
    wellbeing_phrases = [
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
    "how are you feeling today", "how's your overall status", "how's your overall health",
    "how's your life", "how's your day been", "how's your wellbeing today",
    "how are you coping", "how are you feeling right now", "how's your current mood",
    "how's your day shaping up", "how's everything on your end", "how's your day treating you",
    "how's your mood today", "how's your mental health", "how's your overall wellbeing",
    "how are things going with you", "how's your state of mind", "how are you holding up today",
    "how's everything in your world", "how are you managing today", "how's your emotional state",
    "how's your overall mood", "how are you feeling at the moment", "how's your day so far",
    "how are things with you today", "how are you feeling overall", "how's your mood lately",
    "how's your day going so far", "how's your mental health today", "how's your overall condition",
    "how are you coping today", "how's everything in your life", "how's your mental wellbeing",
    "how are you managing emotionally", "how are you doing mentally", "how's your day treating you so far",
    "how's your general state", "how are things going today", "how are you doing emotionally",
    "how's everything in your day", "how's your emotional wellbeing", "how's your mood at the moment",
    "how are you feeling emotionally", "how's everything with you today", "how's your mental state today"
    ]


    # Hate messages
    hate_messages_phrases = [
    "you're stupid", "you're an idiot", "you're dumb", "you're worthless", "you're a fool",
    "you're a moron", "you're an imbecile", "you're a jerk", "you're a loser", "you're pathetic",
    "you're useless", "you're a disgrace", "you're a failure", "you're a dimwit", "you're a simpleton",
    "you're a clod", "you're a nitwit", "you're a blockhead", "you're an ignoramus", "you're a buffoon",
    "you're a nincompoop", "you're a dolt", "you're a dolt", "you're an ass", "you're a jerk",
    "you're a nitwit", "you're a simpleton", "you're a blockhead", "you're a halfwit", "you're a dope",
    "you're a numskull", "you're a knucklehead", "you're a nitwit", "you're a dullard", "you're a ninny",
    "you're a dullard", "you're a dimwit", "you're a fool", "you're a clueless idiot", "you're an ignoramus",
    "you're a simpleton", "you're a halfwit", "you're a nincompoop", "you're a clueless moron",
    "you're a clueless dolt", "you're a clueless blockhead", "you're a brainless twit", "you're a stupid idiot",
    "you're an obnoxious idiot", "you're a pitiful fool", "you're an irritating imbecile", "you're an annoying moron",
    "you're a mindless buffoon", "you're a pointless dolt", "you're a pathetic ignoramus", "you're an irritating nitwit",
    "you're an insignificant idiot", "you're a feeble-minded fool", "you're a mindless imbecile", "you're a ridiculous blockhead",
    "you're a laughable moron", "you're a pitiful dolt", "you're a laughable nincompoop", "you're an inconsequential idiot",
    "you're a laughable simpleton", "you're a ridiculous halfwit", "you're an inconsequential fool", "you're a ridiculous twit",
    "you're a trivial idiot", "you're a laughable ignoramus", "you're a pitiful nitwit", "you're a laughable brainless moron",
    "you're an insignificant dolt", "you're a laughable buffoon", "you're an inconsequential imbecile", "you're a laughable dope",
    "you're a trivial ninny", "you're a laughable dullard", "you're a laughable halfwit", "you're an insignificant moron",
    "you're a trivial nincompoop", "you're an inconsequential brainless idiot", "you're a laughable silly goose",
    "you're a worthless nincompoop", "you're a feeble-minded twit", "you're an insignificant idiot", "you're a trivial nitwit",
    "you're a laughable dimwit", "you're an inconsequential dolt", "you're a laughable knucklehead", "you're an inconsequential fool",
    "you're an insignificant ignoramus", "you're a laughable nitwit", "you're an inconsequential imbecile", "you're a trivial twit",
    "you're a laughable dolt", "you're an inconsequential halfwit", "you're an insignificant ninny", "you're a trivial moron",
    "you're a laughable brainless blockhead", "you're a worthless fool", "you're a pitiful dolt", "you're a trivial blockhead",
    "you're a laughable silly goose", "you're an insignificant dimwit", "you're a trivial idiot", "you're an inconsequential nitwit",
    "you're a laughable ignoramus", "you're a worthless halfwit", "you're an insignificant brainless dolt", "you're a trivial moron",
    "you're a laughable silly goose", "you're a pitiful nincompoop", "you're a trivial nitwit", "you're a laughable blockhead",
    "you're a worthless idiot", "you're an inconsequential nincompoop", "you're a laughable dolt", "you're an insignificant twit"
    ]


    # Compliments phrases
    compliments_phrases = [
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
    "you are very charming", "you are very captivating", "you have a magnetic personality",
    "you are a delight", "you're exceptional", "you have a lovely demeanor", 
    "you're a breath of fresh air", "you're a star", "you're fantastic", "you're stellar",
    "you radiate positivity", "you're a joy to be around", "you have a great sense of humor",
    "you're very dynamic", "you're so admirable", "you're a treasure", "you have a great energy",
    "you're so admirable", "you're incredibly kind", "you've got great taste", "you are very graceful",
    "you're a gem", "you're quite remarkable", "you're very impressive", "you're absolutely amazing",
    "you have a warm personality", "you bring joy wherever you go", "you're a real gem", 
    "you're absolutely delightful", "you're wonderfully creative", "you have a unique charm",
    "you're an extraordinary person", "you have an incredible talent", "you have an amazing presence"
    ]


    # Farewell phrases
    farewell_phrases = [
    "goodbye", "bye", "exit", "see you", "see you later", "farewell", "take care",
    "catch you later", "later", "adios", "ciao", "au revoir", "so long", "see ya",
    "peace out", "i'm out", "talk to you later", "until next time", "until we meet again",
    "have a good day", "have a nice day", "have a great day", "see you soon",
    "bye-bye", "take it easy", "have a good one", "stay safe", "take care of yourself", 
    "cya", "tata", "good night", "have a nice evening", "have a good night", "so long",
    "see you later alligator", "after a while crocodile", "until then", "goodbye for now",
    "have a pleasant day", "catch you later alligator", "take it easy tiger", "farewell for now",
    "goodbye and take care", "bye for now", "see you later alligator", "catch you on the flip side",
    "have a nice one", "goodbye and stay safe", "see you around", "goodbye and have a good one",
    "see you soon, take care", "until we speak again", "bye now", "cheers", "later gator",
    "goodbye and have a great day", "see you next time", "goodbye, take care of yourself",
    "goodbye and stay healthy", "take care and see you soon", "goodbye and have a nice evening",
    "goodbye and have a great night", "bye, take care", "goodbye and talk soon",
    "goodbye, see you later", "take care and stay safe", "goodbye, until next time",
    "farewell, have a nice day", "goodbye, stay well", "see you soon and take care",
    "goodbye, have a pleasant day", "goodbye and have a wonderful day", "take care and see you soon",
    "see you later, have a great day", "goodbye, have a good one", "until next time, goodbye",
    "goodbye, see you around", "take care, see you soon", "goodbye and have a fantastic day",
    "farewell, until we meet again", "see you later, take care", "goodbye and stay safe"
    ]
   # Small Talk phrases
    small_talk_phrases = [
        "what's your favorite", "do you like", "what do you think about", "tell me about",
        "what are your thoughts on", "have you heard about", "what's new with you",
        "what's interesting", "do you know about", "what's going on"
    ]

    # Requests phrases
    requests_phrases = [
        "can you", "could you", "please", "help me with", "assist me with", "I need help with",
        "can you provide", "please tell me", "could you help with", "I'm looking for"
    ]

    # Gratitude phrases
    gratitude_phrases = [
        "thank you", "thanks", "I appreciate it", "I'm grateful", "many thanks",
        "thank you very much", "thanks a lot", "thanks a million", "I owe you one"
    ]

    # Apologies phrases
    apologies_phrases = [
        "sorry", "I apologize", "my bad", "excuse me", "pardon me", "I didn't mean to",
        "please forgive me", "I regret", "I'm sorry for", "I hope you can forgive me"
    ]

    # Confusion phrases
    confusion_phrases = [
        "I don't understand", "can you explain", "what do you mean", "I'm confused", "I'm not sure",
        "could you clarify", "what does that mean", "I'm not clear on", "can you elaborate"
    ]

    # Check if the sentence matches any of the categories
    if any(re.search(phrase, sentence) for phrase in wellbeing_phrases):
        return "wellbeing"
    if any(re.search(phrase, sentence) for phrase in hate_messages_phrases):
        return "hate_message"
    if any(re.search(phrase, sentence) for phrase in compliments_phrases):
        return "compliments"
    if any(re.search(phrase, sentence) for phrase in farewell_phrases):
        return "farewell"
    if any(re.search(phrase, sentence) for phrase in small_talk_phrases):
        return "small_talk"
    if any(re.search(phrase, sentence) for phrase in requests_phrases):
        return "request"
    if any(re.search(phrase, sentence) for phrase in gratitude_phrases):
        return "gratitude"
    if any(re.search(phrase, sentence) for phrase in apologies_phrases):
        return "apology"
    if any(re.search(phrase, sentence) for phrase in confusion_phrases):
        return "confusion"

    # Check if the sentence matches any of the categories
    if any(re.search(phrase, sentence) for phrase in wellbeing_phrases):
        return "wellbeing"
    if any(re.search(phrase, sentence) for phrase in hate_messages_phrases):
        return "hate_message"
    if any(re.search(phrase, sentence) for phrase in compliments_phrases):
        return "compliments"
    if any(re.search(phrase, sentence) for phrase in farewell_phrases):
        return "farewell"

    # Extended list of common greetings
    greetings = [
        r'hi', r'hello', r'hey', r'greetings', r'morning', r'evening', r'good morning', 
        r'good afternoon', r'good evening', r'what\'s up', r'howdy', r'what\'s happening', 
        r'hi there', r'hello there', r'hey there', r'yo', r'hiya', r'hey hey', 
        r'how\'s it going', r'how are you', r'what\'s new', r'howdy doo', r'sup', 
        r'hiya', r'hey buddy', r'hey there pal', r'hey there mate', r'hello mate', 
        r'hello friend', r'good day', r'good to see you', r'long time no see', 
        r'hey stranger', r'how are ya', r'what\'s going on', r'what\'s cracking', 
        r'what\'s up dude', r'hey dude', r'hey man', r'hey woman', r'hi man', 
        r'hi woman', r'hello everyone', r'hi everyone', r'hello all', r'hi all', 
        r'hi folks', r'hello folks', r'hi friends', r'hello friends', r'hey everyone', 
        r'good to see you again', r'hi guys', r'hello guys', r'what\'s up guys', 
        r'hey guys', r'how\'s everything', r'hey there everyone', r'hello there everyone', 
        r'what\'s going on guys', r'hey peeps', r'hello peeps', r'what\'s up peeps', 
        r'hey y\'all', r'hello y\'all', r'what\'s up y\'all', r'hey fam', 
        r'hello fam', r'what\'s up fam', r'hey all', r'hello all', r'hi all', 
        r'hello world', r'hey world', r'good to see you', r'hey there', r'how\'s everything going'
    ]



        # Check for common question words if no specific category matches
    question_keywords = ['who', 'what', 'where', 'when', 'why', 'how']
    if any(word in sentence for word in question_keywords):
        return "question"
           # Check if the sentence matches any of the greetings
    if any(re.search(greeting, sentence) for greeting in greetings):
        return "greeting" 

    # Default to "statement" if no specific category matches
    return "statement"

def is_weather_question(query):
    weather_keywords = ["weather", "temperature", "forecast", "rain", "snow", "sunny", "cloudy"]
    return any(keyword in query.lower() for keyword in weather_keywords)

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

# Function to search and provide an answer based on the command
def parse_and_execute_command(command):
    command = command.lower()
    classification = classify_sentence(command)
    now = datetime.datetime.now()
#convo 
    # Greetings
    if classification == "greeting":
        responses = [
        "Hello! How can I assist you today?",
        "Hi there! What can I do for you?",
        "Hey! How's it going?",
        "Greetings! How can I help you today?",
        "Good day! What do you need assistance with?",
        "Hello! What can I help you with today?",
        "Hi! How's everything on your end?",
        "Hey there! How can I be of service?",
        "Hello! What can I do for you right now?",
        "Hi! How can I assist you today?",
        "Greetings! What brings you here today?",
        "Hey! What do you need help with?",
        "Hello there! How can I support you?",
        "Hi! Is there anything you need assistance with?",
        "Hey! What can I help you with?",
        "Hello! How's your day going so far?",
        "Hi there! How can I make your day better?",
        "Greetings! How can I assist you today?",
        "Hey there! What can I do for you today?",
        "Hello! How can I be helpful?",
        "Hi! What’s on your mind today?",
        "Hey! How’s everything going?",
        "Hello! What’s up?",
        "Hi! How can I assist you at this moment?",
        "Hey there! What’s new with you?",
        "Hello! What can I help you with right now?",
        "Hi there! What do you need today?",
        "Greetings! How can I be of help?",
        "Hey! What’s your need today?",
        "Hello! How’s everything on your end?",
        "Hi! What can I do for you today?",
        "Hey there! How can I assist you today?",
        "Hello! What’s your request?",
        "Hi! How can I support you today?",
        "Hey! How can I be of service to you?",
        "Greetings! What’s up?",
        "Hello! How’s your day treating you?",
        "Hi there! What can I assist with today?",
        "Hey! What can I help with?",
        "Hello! How can I make your day easier?",
        "Hi! How’s it going today?",
        "Hey there! How can I be helpful?",
        "Hello! What do you need assistance with today?",
        "Hi! How can I assist you?",
        "Hey! What’s new with you today?",
        "Hello! How can I help you out?",
        "Hi there! What’s on your mind?",
        "Greetings! What do you need help with?",
        "Hey! How can I be of assistance?",
        "Hello! What’s the matter?",
        "Hi! How can I support you?",
        "Hey there! What can I do for you today?"
    ]
        response = random.choice(responses)
        print(response)
        return
    elif "are you talking back" in command:
        print("Thats how conversation works..")
        return
    
    # Wellbeing
    if classification == "wellbeing":
        responses = [
            "I'm just a program, but I'm here to help you! How can I assist you today?",
            "I'm doing great, thanks for asking! How can I support you today?",
            "I'm here to help! How are you feeling?",
            "I'm here and ready to assist you. How's your day going?",
            "Thank you for asking! How can I make your day better?"
        ]
        response = random.choice(responses)
        print(response)
        return
    
    # Emotional Support
    if classification == "emotional_support":
        responses = [
            "I'm sorry to hear that you're feeling this way. Remember, it's okay to seek support from friends or professionals.",
            "I'm here for you. If you need someone to talk to, I'm always available.",
            "I understand things can be tough. Try to take things one step at a time, and don't hesitate to seek help if needed.",
            "It's okay to feel down sometimes. If you want to talk about it, I'm here to listen.",
            "Remember, you're not alone. There are people who care about you and want to help."
        ]
        response = random.choice(responses)
        print(response)
        return
    
    if "what's the weather like in" in command or "weather in" in command or "hows the climate in" in command or "climate in" in command or "whats the weather in" in command:
        city_name = command.split("in")[-1].strip()
        weather_info = get_weather(city_name)
        print(weather_info)
        return
        
    # Hate Messages
    if classification == "hate_message":
        responses = [
            "I'm here to assist, and I'd appreciate if we keep things positive. How can I help you today?",
            "Let's focus on finding solutions and positive outcomes. How can I assist you?",
            "I understand you might be frustrated, but let's try to keep our interactions respectful.",
            "I'm here to help with any issues you may have. How can I support you today?",
            "Let's work on resolving this in a constructive way. How can I assist you?"
        ]
        response = random.choice(responses)
        print(response)
        return
    
    # Compliments
    if classification == "compliments":
        responses = [
            "Thank you for the compliment! I'm here to assist you in any way I can.",
            "I appreciate your kind words! How can I help you further?",
            "You're very kind! How can I assist you today?",
            "Thank you! I'm here to provide support and assistance.",
            "Your words are appreciated! How can I make your day better?"
        ]
        response = random.choice(responses)
        print(response)
        return
    
    # Responses for "what is your name" and "who are you"
    if "what is your name" in command or "who are you" in command:
        responses = [
            f"I am {assistant_name}, your assistant.",
            f"Hey, I'm {assistant_name}. How can I help you today?",
            f"My name is {assistant_name}. What can I do for you?",
        ]
        print(random.choice(responses))
        return
    
    if any(phrase in command for phrase in ["What’s your favorite color", "What is your favorite color", "What color do you like"]):
     responses = [
        "I love the color red!",
        "Red is definitely my favorite!",
        "I'm a big fan of the color red!",
        "Red suits me best!",
        "I really like red, it's vibrant!"
     ]
     print(random.choice(responses))
         
    # Responses for 'change your name' and 'rename you'
    if 'change your name' in command or 'rename you' in command:
        responses = [
            f"As an AI, I don't have a name that I can change. I'm happy to continue responding to your requests as {assistant_name}. 😊",
            f"Sorry, I can't change my name. You can call me {assistant_name}!",
            f"I'm {assistant_name} and I'm here to help. My name stays the same! 😊",
        ]
        print(random.choice(responses))
        return

    # Responses for "your name"
    if "your name" in command:
        responses = [
            f"I am {assistant_name}, your assistant.",
            f"You can call me {assistant_name}. How can I assist you?",
            f"My name is {assistant_name}. What do you need?",
        ]
        print(random.choice(responses))
        return

    # Responses for "are you a human"
    if "are you a human" in command:
        responses = [
            "Nope, I'm not a human. I'm a Virtual Girl.",
            "I'm an AI, not a human.",
            "I'm a virtual assistant, not a human!",
            "You wish i was."
        ]
        print(random.choice(responses))
        return

    # Responses for "what is your gender"
    if "what is your gender" in command:
        responses = [
            "My gender is she/her.",
            "I use she/her pronouns.",
            "You can refer to me using she/her pronouns.",
        ]
        print(random.choice(responses))
        return

    # Responses for "are you batman"
    if "are you batman" in command or "do you know batman" in command:
        responses = [
            "Yes, I'm BATMAN! Gotham City needs me.",
            "Absolutely, I'm BATMAN. What’s the mission?",
            "Yes, I’m BATMAN. Ready to fight crime!",
        ]
        print(random.choice(responses))
        return
    
    elif "who is your favorite singer" in command or "who is your fav singer" in command:
        print("Its the guy from umm... the song which goes like NEVER GONNA GIVE YOU UP NEVER GONNA LET YOU DOWN.")
        return

    if 'who are you' in command.lower() or 'what is your name' in command.lower():
        responses = [
            f"Hello! I am {assistant_name}, your advanced AI assistant. My purpose is to help you with a variety of tasks, from answering questions to managing your schedule. I was created by {creator_name}, and I'm here to make your life easier and more enjoyable.",
            f"I'm {assistant_name}, your personal assistant designed to assist with a range of tasks. Created by {creator_name}, I'm here to make your day a bit easier and more efficient.",
            f"Hi there! I'm {assistant_name}, and I was built by {creator_name}. I'm here to help you with whatever you need, from answering your questions to managing your daily tasks.",
            f"Greetings! I am {assistant_name}, an AI assistant created by {creator_name}. My goal is to assist you in various tasks and provide you with useful information.",
            f"Hey! I'm {assistant_name}, your AI assistant. Designed by {creator_name}, I'm here to help you with a wide range of activities and make your life simpler."
        ]
        response = random.choice(responses)
        print(response)
        return
    
    # Check for dictionary lookup requests
    # List of patterns for defining a word
    patterns = [
        r'what is the meaning of (\w+)',
        r'what does (\w+) mean',
        r'meaning of (\w+)',
        r'definition of (\w+)',
        r'define (\w+)',
        r'give me the definition of (\w+)',
        r'tell me the meaning of (\w+)',
        r'how do you define (\w+)'
    ]

    # Check for dictionary lookup requests
    match = None
    for pattern in patterns:
        match = re.match(pattern, command)
        if match:
            break
    if match:
        word = match.group(1)
        definition = search_word_in_dictionary(word)
        if definition:
            print(f"The definition of '{word}' is: {definition}")
        else:
            definition = search_and_provide_answer(word)
            if definition:
                print(f"The definition of '{word}' is: {definition}")
                update_dictionary(word, definition)
            else:
                print(f"I couldn't find the definition of '{word}'.")
        return
        

    # Farewell
    elif classification == "farewell":
        responses = [
            "Goodbye! Have a great day!",
            "Farewell! If you need assistance again, I'll be here.",
            "Take care! See you next time.",
            "Goodbye! It was nice talking to you.",
            "See you later! Have a wonderful day!"
        ]
        response = random.choice(responses)
        print(response)
        return
    
    if "full form of nira" in command:
        print("Neural Advanced Interactive Network Assistant")
        return
         
    if "help" in command :
        print("The more information you give me, the better I can understand your needs and provide useful help. Please tell me more! I need more information to be helpful")
        return
    
    if "what it your age" in command:
        print("Im 21 years old. Tho i was borned on 15 sept 2022")
    
    if "how old are you" in command:
        print("Im 21 years old. Tho i was borned on 15 sept 2022")
    
    if random.random() < 0.01:
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley")
        return
       
    if "calculate" in command:
        try:
            expression = command.split("calculate")[1].strip()
            result = eval(expression)
            print(f"The result of {expression} is {result}")
        except Exception as e:
            print(f"Sorry, I couldn't calculate that. Error: {e}")
        return
    
    if "who is your creator" in command:
        print(f"I'm created by {creator_name}")
        return
            
    if "who created you" in command:
        print(f"I'm created by {creator_name}")
        return
            
    if "who made you" in command:
        print(f"I'm created by {creator_name}")
        return
            
    elif "flip a coin" in command:
        result = flip_coin()
        print(f"The result is: {result}")
        return        
        
    if "tell me a joke" in command or "joke" in command:
        joke = fetch_joke()
        print(joke)
        return
    
    elif "tell me about" in command:
        topic = command.split("about")[-1].strip()
        search_and_provide_answer(f"What is {topic}")
        return
            
    elif 'bruh' in command.lower():
        responses = [
            "Oops! Did I mess up? Let me know how I can improve.",
            "Bruh! That was unexpected. How can I make it better?",
            "Looks like I might have made a mistake. Any suggestions?",
            "Well, that’s awkward. How can I assist you better?",
            "I guess I goofed up. What should I do differently?"
        ]
        response = random.choice(responses)
        print(response)
        return

        
    # Time-related responses
    if 'what is the time' in command or 'tell me the time' in command or 'current time' in command or 'time now' in command or 'what time is it' in command:
        strTime = now.strftime("%H:%M:%S")
        print(f"The time is {strTime}")
        return
    
    # Day-related responses
    if 'what is the day' in command or 'today\'s day' in command or 'current day' in command or 'which day is it' in command:
        strDay = now.strftime("%A")
        print(f"The day is {strDay}")
        return
        
    # Date-related responses
    if 'what is the date' in command or 'tell me the date' in command or 'current date' in command or 'today\'s date' in command:
        strDate = now.strftime("%Y-%m-%d")
        print(f"The date is {strDate}")
        return
    
    # Month-related responses
    if 'what is the month' in command or 'current month' in command or 'which month is it' in command:
        strMonth = now.strftime("%B")
        print(f"The month is {strMonth}")
        return
        
    # Year-related responses
    if 'what is the year' in command or 'current year' in command or 'which year is it' in command:
        strYear = now.strftime("%Y")
        print(f"The year is {strYear}")
        return

    elif classification == "question":
        search_and_provide_answer(command)
        return

        
    else:
        search_and_provide_answer(command)
        return

    # After answering, wait for the next command



# Function to analyze sentiment of text using a pretrained model
def analyze_sentiment(text):
    try:
        # Use your NLP model for sentiment analysis
        return "Positive"  # Replace with actual sentiment analysis logic
    except Exception as e:
        return "Error analyzing sentiment."
       
# Function to provide a recommendation based on user input
def provide_recommendation(recommendation_type):
    try:
        # Provide recommendation based on user input
        print(f"Here is a recommendation for {recommendation_type}.")
        return(f"Here is a recommendation for {recommendation_type}.")# Replace with actual recommendation logic
    except Exception as e:
        print(f"Sorry, I couldn't provide a recommendation for {recommendation_type}. Error: {e}")
        return(f"Sorry, I couldn't provide a recommendation for {recommendation_type}. Error: {e}")
            
#for coin flips
def flip_coin():
    result = random.choice(["Heads", "Tails"])
    return result

# Main function to run the assistant
def run_assistant():
    greet_user()
    
    while True:
        command = input("Enter your command: ").strip()
        if command:
            parse_and_execute_command(command)
        else:
            print("No command received. Please try again.")
            return
            
# Start the assistant
if __name__ == "__main__":
    run_assistant()
