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
from dateutil import parser as date_parser
import google.generativeai as genai
import re
from google.api_core.exceptions import InternalServerError

#==API==#
# Install newsapi-python library
genai.configure(api_key='YOUR API')
model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')
chat = model.start_chat()

#creator / AI name
assistant_name = "Nira"
creator_name = "Voidware labs"

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
        "how's your status", "how's your condition", "how do you feel today", 
        "how you been", "how are you feeling", "what's new", "how's your energy", 
        "how's it hanging", "how's your vibe", "how's your spirit", "how are you faring", 
        "how do you do", "how are you holding on", "how's your mental state", 
        "how's your wellbeing", "how's everything going", "how's your health", 
        "how's your day going", "how's your system running", "what's your status", 
        "what's your state", "how's the system", "how's your functionality", 
        "how's your performance", "how's your operating status", "how are you operating", 
        "how are you functioning", "how are you managing", "how's your disposition", 
        "how's your outlook", "how are you feeling today", "how's your overall status", 
        "how's your overall health", "how's your life", "how's your day been", 
        "how's your wellbeing today", "how are you coping", "how are you feeling right now", 
        "how's your current mood", "how's your day shaping up", "how's everything on your end", 
        "how's your day treating you", "how's your mood today", "how's your mental health", 
        "how's your overall wellbeing", "how are things going with you", "how's your state of mind", 
        "how are you holding up today", "how's everything in your world", 
        "how are you managing today", "how's your emotional state", "how's your overall mood", 
        "how are you feeling at the moment", "how's your day so far", "how are things with you today", 
        "how are you feeling overall", "how's your mood lately", "how's your day going so far", 
        "how's your mental health today", "how's your overall condition", "how are you coping today", 
        "how's everything in your life", "how's your mental wellbeing", "how are you managing emotionally", 
        "how are you doing mentally", "how's your day treating you so far", "how's your general state", 
        "how are things going today", "how are you doing emotionally", "how's everything in your day", 
        "how's your emotional wellbeing", "how's your mood at the moment", "how are you feeling emotionally", 
        "how's everything with you today", "how's your mental state today"
    ]

    # Hate messages
    hate_phrases = [
     "i hate you", "i don't like you", "you're annoying", "you suck", 
     "you're the worst", "i can't stand you", "you’re so irritating", 
     "you’re terrible", "i wish you weren't here", "you’re so useless", 
     "i dislike you", "you're so dumb", "you’re so frustrating", 
     "i can't deal with you", "you’re a bother", "you’re a nuisance", 
     "i don't want to talk to you", "you’re such a pain", "you’re a burden", 
     "you’re not helpful", "i’m fed up with you", "you’re so frustrating", 
     "you’re annoying me", "i wish you would leave", "you’re driving me crazy", 
     "you’re so bothersome", "i’m done with you", "you’re a hassle", 
     "you’re a drag", "i don't want to deal with you", "you’re such a hassle", 
     "you’re a total letdown", "you’re getting on my nerves", "you’re useless", 
     "you’re such a disappointment", "i can’t stand talking to you", 
     "you’re a pain in the neck", "you’re so aggravating", "you’re really getting to me", 
     "you’re just not helpful", "i can’t handle you", "you’re not worth my time", 
     "you’re just a hassle", "i’m over you", "you’re such a letdown",
     "you're stupid", "you're an idiot", "you're dumb", "you're worthless", 
     "you're a fool", "you're a moron", "you're an imbecile", "you're a jerk", 
     "you're a loser", "you're pathetic", "you're useless", "you're a disgrace", 
     "you're a failure", "you're a dimwit", "you're a simpleton", "you're a clod", 
     "you're a nitwit", "you're a blockhead", "you're an ignoramus", "you're a buffoon", 
     "you're a nincompoop", "you're a dolt", "you're an ass", "you're a halfwit", 
     "you're a dope", "you're a numskull", "you're a knucklehead", "you're a dullard", 
     "you're a ninny", "you're a clueless idiot", "you're a clueless moron", 
     "you're a clueless dolt", "you're a brainless twit", "you're an obnoxious idiot", 
     "you're a pitiful fool", "you're an irritating imbecile", "you're an annoying moron", 
     "you're a mindless buffoon", "you're a pointless dolt", "you're a pathetic ignoramus", 
     "you're an irritating nitwit", "you're an insignificant idiot", "you're a feeble-minded fool", 
     "you're a mindless imbecile", "you're a ridiculous blockhead", "you're a laughable moron", 
     "you're a pitiful dolt", "you're a laughable nincompoop", "you're an inconsequential idiot", 
     "you're a laughable simpleton", "you're a ridiculous halfwit", "you're an inconsequential fool", 
     "you're a ridiculous twit", "you're a trivial idiot", "you're a laughable ignoramus", 
     "you're a pitiful nitwit", "you're a laughable brainless moron", "you're an insignificant dolt", 
     "you're a laughable silly goose", "you're a worthless nincompoop", "you're a feeble-minded twit", 
     "you're an insignificant idiot", "you're a trivial nitwit", "you're a laughable dimwit", 
     "you're an inconsequential dolt", "you're a laughable knucklehead", "you're an inconsequential fool", 
     "you're an insignificant ignoramus", "you're a laughable nitwit", "you're an inconsequential imbecile", 
     "you're a trivial twit", "you're a laughable dolt", "you're an inconsequential halfwit", 
     "you're an insignificant ninny", "you're a trivial moron", "you're a laughable brainless blockhead", 
     "you're a worthless fool", "you're a pitiful dolt", "you're a trivial blockhead", 
     "you're a laughable silly goose", "you're an insignificant dimwit", "you're a trivial idiot", 
     "you're an inconsequential nitwit", "you're a laughable ignoramus", "you're a worthless halfwit", 
     "you're an insignificant brainless dolt", "you're a trivial moron", "you're a laughable silly goose", 
     "you're a pitiful nincompoop", "you're a trivial nitwit", "you're a laughable blockhead", 
     "you're a worthless idiot", "you're an inconsequential nincompoop", "you're a laughable dolt", 
     "you're an insignificant twit"
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
        "you are very uplifting", "you are very encouraging", "you always brighten my day",
        "you're a real gem", "you're a real treasure", "you have a great sense of style",
        "you're very fashionable", "you have a great taste", "you have a great sense of humor",
        "you are so thoughtful", "you are very kind-hearted", "you are very empathetic",
        "you have a great attitude", "you have a great demeanor", "you're a great role model"
    ]

    # Emotional support phrases
    emotional_support_phrases = [
     "i feel sad", "i am burnt out", "i'm anxious", "i feel stressed", "i am overwhelmed",
     "i feel lonely", "i'm tired", "i feel hopeless", "i am frustrated", "i feel like giving up",
     "i'm feeling down", "i feel depressed", "i am struggling", "i feel empty", "i am having a tough time",
     "i'm in a bad mood", "i feel lost", "i am feeling blue", "i feel broken", "i am disconnected",
     "i'm dealing with a lot", "i feel drained", "i am at my breaking point", "i feel out of sorts",
     "i'm feeling unsupported", "i feel overwhelmed by stress", "i am emotionally exhausted",
     "i feel stuck in a rut", "i'm struggling to cope", "i feel mentally exhausted", "i am burned out",
     "i feel overwhelmed", "i'm emotionally drained", "i feel out of control", "i am struggling with stress",
     "i feel hopeless", "i'm failing", "i feel like i'm not coping well", "i am isolated" ,
     "i feel like giving up", "i'm dealing with depression", "i feel on edge", "i am overwhelmed with everything", 
     "i feel trapped", "i am emotionally spent", "i feel like i can't keep going", "i am mentally unwell",
     "i feel lost", "i am failing", "i feel like i'm dealing with too much", "i am suffocating",
     "i feel disconnected", "i am emotionally numb", "i feel like i'm not okay", "i am downhearted",
     "i feel in a hole", "i'm having a rough time", "i feel like i'm being pulled down", "i am emotionally overwhelmed",
     "i feel stuck", "i am emotionally low", "i feel like i can't cope", "i am struggling to find motivation",
     "i feel like i'm drowning", "i am feeling heavy", "i feel like i'm on the verge of breaking down",
     "i am emotionally drained", "i feel out of my depth", "i am emotionally unstable", "i feel like i've hit a wall",
     "i'm struggling to stay positive", "i feel like i'm running on empty", "i am worn out", "i feel like i'm losing control",
     "i'm stressed out", "i feel like i'm going through a rough patch", "i am overwhelmed by everything",
     "i feel like i'm at my limit", "i am struggling to handle things", "i feel like i can't handle the pressure",
     "i'm mentally drained", "i feel like i'm falling apart", "i am struggling with stress", "i feel like i'm in a dark place",
     "i am emotionally out of balance", "i feel like i can't get through this", "i am dealing with my emotions",
     "i feel like i'm stuck in a negative cycle", "i am emotionally burdened", "i feel like i'm losing hope",
     "i am struggling to keep it together", "i feel like i'm constantly battling", "i am overwhelmed by my emotions",
     "i feel like i'm barely managing", "i am struggling to stay grounded", "i feel like i'm on the edge",
     "i am emotionally overwhelmed", "i feel like i'm constantly stressed", "i am struggling to find peace",
     "i feel like i'm carrying a heavy weight", "i am mentally exhausted", "i feel like i'm at a breaking point",
     "i am struggling to stay strong", "i feel like i'm losing my way", "i am running on empty", "i feel like i'm barely hanging on",
     "i am struggling with feelings of inadequacy", "i feel like i'm not myself", "i am overwhelmed by daily tasks",
     "i feel like i'm being pushed to my limits", "i am struggling to find balance", "i feel like i'm in a constant battle",
     "i am mentally overwhelmed", "i feel like i'm losing my grip", "i am struggling to find relief", "i feel like i'm stuck in a loop",
     "i am emotionally spent", "i feel like i'm in a state of crisis", "i am struggling with my inner self", "i feel like i'm running on empty",
     "i am emotionally overwhelmed", "i feel like i'm losing control", "i am struggling to stay positive", "i feel like i'm in a state of despair",
     "i am mentally drained", "i feel like i'm not getting anywhere", "i am struggling to cope with stress", "i feel like i'm barely holding on",
     "i am emotionally exhausted", "i feel like i'm in a dark place", "i am struggling to manage my feelings", "i feel like i'm constantly overwhelmed",
     "i am emotionally off-balance", "i feel like i'm losing my direction", "i am struggling to maintain hope", "i feel like i'm not making progress",
     "i am mentally taxed", "i feel like i'm at my limit", "i am struggling with my emotional state", "i feel like i'm running out of energy",
     "i am emotionally vulnerable", "i feel like i'm at a loss", "i am struggling to handle my emotions", "i feel like i'm on the brink",
     "i am mentally exhausted", "i feel like i'm in a bad place", "i am struggling to find a way out", "i feel like i'm overwhelmed by everything",
     "i am emotionally drained", "i feel like i'm losing my way", "i am struggling to stay hopeful", "i feel like i'm barely managing",
     "i am emotionally unsettled", "i feel like i'm constantly on edge", "i am struggling to keep up", "i feel like i'm in a rough spot",
     "i am mentally overwhelmed", "i feel like i'm barely coping", "i am struggling to maintain my emotional health", "i feel like i'm stuck in a rut",
     "i am emotionally exhausted", "i feel like i'm in a crisis", "i am struggling to stay strong", "i feel like i'm losing hope",
     "i am mentally drained", "i feel like i'm at my breaking point", "i am struggling to find peace", "i feel like i'm on the verge of collapse",
     "i am emotionally unwell", "i feel like i'm barely hanging on", "i am struggling to manage my stress", "i feel like i'm in a deep hole",
     "i am mentally depleted", "i feel like i'm constantly battling", "i am struggling with overwhelming emotions", "i feel like i'm running out of steam",
     "i am emotionally strained", "i feel like i'm at my limit", "i am struggling to keep my emotions in check", "i feel like i'm constantly stressed",
     "i am mentally exhausted", "i feel like i'm losing my footing", "i am struggling to stay resilient", "i feel like i'm in a bad place mentally",
     "i am emotionally burned out", "i feel like i'm not making headway", "i am struggling to manage my mental health", "i feel like i'm stuck in a negative cycle",
     "i am emotionally frazzled", "i feel like i'm running on empty", "i am struggling to cope with life", "i feel like i'm constantly on the verge",
     "i am mentally fatigued", "i feel like i'm losing my way", "i am struggling with my mental state", "i feel like i'm overwhelmed by my feelings",
     "i am emotionally spent", "i feel like i'm on the edge", "i am struggling to find relief", "i feel like i'm at a breaking point",
     "i am emotionally drained", "i feel like i'm barely managing", "i am struggling with mental fatigue", "i feel like i'm in a dark place",
     "i am emotionally strained", "i feel like i'm barely holding on", "i am struggling to stay afloat", "i feel like i'm in a rough spot emotionally",
     "i am mentally taxed", "i feel like i'm on the verge of collapse", "i am struggling to cope with my feelings", "i feel like i'm losing hope",
     "i am emotionally unstable", "i feel like i'm in a crisis", "i am struggling to stay positive", "i feel like i'm overwhelmed by stress",
     "i am emotionally fragile", "i feel like i'm stuck in a rut", "i am struggling to keep going", "i feel like i'm constantly battling my emotions",
     "i am mentally exhausted", "i feel like i'm not myself", "i am struggling to handle my stress", "i feel like i'm at my breaking point",
     "i am emotionally drained", "i feel like i'm constantly overwhelmed", "i am struggling with my emotional well-being", "i feel like i'm stuck in a negative cycle",
     "i am mentally depleted", "i feel like i'm in a bad place"
     ]
    
    
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
    
    apologies_phrases = [
        "sorry", "I apologize", "my bad", "excuse me", "pardon me", "I didn't mean to",
        "please forgive me", "I regret", "I'm sorry for", "I hope you can forgive me"
    ]

    # Function to check for overlap between categories
    def has_overlap(category, other_categories):
        for other_category in other_categories:
            if any(phrase in other_category for phrase in category):
                return True
        return False

    # Check for overlap
    hate_overlap = has_overlap(hate_phrases, [wellbeing_phrases, compliments_phrases, emotional_support_phrases])
    wellbeing_overlap = has_overlap(wellbeing_phrases, [hate_phrases, compliments_phrases, emotional_support_phrases])
    compliments_overlap = has_overlap(compliments_phrases, [wellbeing_phrases, hate_phrases, emotional_support_phrases])
    emotional_support_overlap = has_overlap(emotional_support_phrases, [wellbeing_phrases, hate_phrases, compliments_phrases])
    greetings_overlap = has_overlap(greetings, [wellbeing_phrases, hate_phrases, compliments_phrases, emotional_support_phrases])
    apologies_phrases_overlap = has_overlap(apologies_phrases, [wellbeing_phrases, hate_phrases, compliments_phrases, emotional_support_phrases, greetings])

    # Classification logic
    if any(phrase in sentence for phrase in wellbeing_phrases):
        return "wellbeing"
    if any(phrase in sentence for phrase in hate_phrases):
        return "hate_message"
    if any(phrase in sentence for phrase in compliments_phrases):
        return "compliments"
    if any(phrase in sentence for phrase in emotional_support_phrases):
        return "emotional_support"
            # Check for common question words if no specific category matches
    if any(re.search(phrase, sentence) for phrase in farewell_phrases):
        return "farewell"
    if any(re.search(phrase, sentence) for phrase in apologies_phrases):
        return "apologies_phrases"
    question_keywords = ['who', 'what', 'where', 'when', 'why', 'how']
    
    if any(word in sentence for word in question_keywords):
        return "question"
           # Check if the sentence matches any of the greetings
    # Default to "statement" if no specific category matches


    if any(re.search(greeting, sentence) for greeting in greetings):
        return "greeting" 
    
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

# Define the path to the JSON file where requests are stored
REQUESTS_FILE = r'C:\Users\Admin\Desktop\AI\user_request.json'
ALERT_TIME_DELTA = datetime.timedelta(minutes=5)  # Set alert 5 minutes before the scheduled time

def load_requests():
    """Load user requests from the JSON file."""
    if os.path.exists(REQUESTS_FILE):
        try:
            with open(REQUESTS_FILE, 'r') as file:
                content = file.read().strip()  # Read and remove any surrounding whitespace
                if content:  # Check if the content is not empty
                    return json.loads(content)
                else:
                    return []  # Return an empty list if the file is empty
        except json.JSONDecodeError:
            # Handle the case where the file is not valid JSON
            print("Error: JSON file is corrupted. Initializing with an empty list.")
            return []
    else:
        return []

def save_requests(requests):
    """Save user requests to the JSON file."""
    with open(REQUESTS_FILE, 'w') as file:
        json.dump(requests, file, indent=4)

def add_request(user_id, request_text, schedule_datetime):
    """Add a new request to the JSON file."""
    requests = load_requests()
    requests.append({
        'user_id': user_id,
        'request_text': request_text,
        'schedule_datetime': schedule_datetime.isoformat(),  # Store datetime in ISO format
        'alerted': False,  # Track if alert has been given before time
        'alerted_at_time': False  # Track if alert has been given at the scheduled time
    })
    save_requests(requests)

def remove_expired_requests():
    """Remove requests from the JSON file where the schedule time has passed."""
    requests = load_requests()
    now = datetime.datetime.now()
    updated_requests = [req for req in requests if datetime.datetime.fromisoformat(req['schedule_datetime']) > now]
    if len(requests) != len(updated_requests):
        save_requests(updated_requests)  # Save only if there is a change

def execute_scheduled_requests():
    """Check and execute scheduled requests if their time has come."""
    requests = load_requests()
    now = datetime.datetime.now()
    for request in requests:
        schedule_time = datetime.datetime.fromisoformat(request['schedule_datetime'])
        alert_time = schedule_time - ALERT_TIME_DELTA

        # Alert before the scheduled time
        if not request.get('alerted') and now >= alert_time and now < schedule_time:
            print(f"Alert: You have a scheduled event: '{request['request_text']}' at {schedule_time.strftime('%I:%M %p')}")
            request['alerted'] = True  # Mark as alerted before time
            save_requests(requests)  # Save the updated state

        # Alert at the scheduled time
        elif not request.get('alerted_at_time') and now >= schedule_time:
            print(f"Reminder: It is now time for '{request['request_text']}'!")
            request['alerted_at_time'] = True  # Mark as alerted at time
            save_requests(requests)  # Save the updated state

    # After processing, remove expired requests
    remove_expired_requests()

def check_schedules():
    """Check and display all scheduled requests."""
    requests = load_requests()
    if not requests:
        print("No scheduled requests found.")
    else:
        print("Scheduled Requests:")
        for request in requests:
            schedule_time = datetime.datetime.fromisoformat(request['schedule_datetime'])
            print(f"User ID: {request['user_id']}, Request: {request['request_text']}, Scheduled Time: {schedule_time}")

def clear_schedules():
    """Clear all scheduled requests."""
    save_requests([])  # Save an empty list to clear all requests
    print("All scheduled requests have been cleared.")


# Function to search and provide an answer based on the command
def parse_and_execute_command(command):
    command = command.lower()
    classification = classify_sentence(command)
    now = datetime.datetime.now()
    
    if "What’s your favorite color" in command or "What is your favorite color" in command or "What color do you like" in command or "whats your favorite color" in command:
     responses = [
        "I love the color red! It’s so vibrant and lively. ❤️",
        "Red is my favorite color! It’s full of energy and passion. 🌟",
        "I’m a big fan of red! It’s such a dynamic and exciting color. 🔴",
        "Red suits me best! It’s bold and bright. 😄",
        "I really like red. It’s vibrant and stands out beautifully! 🌈"
     ]
     response = random.choice(responses)
     print(response)
     return
 
    # Add Curiosity and Exploration
    if "tell me something interesting" in command or "fun fact" in command:
     responses = [
        "Did you know that honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still good to eat! 🍯",
        "Octopuses have three hearts! Two pump blood to the gills, and the third pumps it to the rest of the body. 🐙",
        "Fun fact: Bananas are technically berries, but strawberries aren’t! 🍌🍓",
        "The Eiffel Tower can be 15 cm taller during the summer due to the iron expanding in the heat. 🌞",
        "Here’s a fun fact: A day on Venus is longer than a year on Venus! 🌍"
     ]
     response = random.choice(responses)
     print(response)
     return

    
    # Feedback
    if any(phrase in command for phrase in [
    "where can i report a bug", "how can i give feedback", "bug report", "feedback submission", "report a problem"]):
     responses = [
        "You can report bugs or provide feedback on our GitHub page: https://github.com/NightBlobby/N.I.R.A. 🐛",
        "To give feedback or report a bug, please visit our GitHub page at https://github.com/NightBlobby/N.I.R.A. 💻",
        "For any bug reports or feedback, head over to our GitHub page: https://github.com/NightBlobby/N.I.R.A. 📝",
        "Submit your feedback or report issues on our GitHub page: https://github.com/NightBlobby/N.I.R.A. 🚀"
     ]
     response = random.choice(responses)
     print(response)
     return

    
    # Add Feedback and Support
    if "need help" in command or "support" in command:
     responses = [
        "I’m here to help! What do you need support with today? 😊",
        "Feel free to ask me anything. I’m ready to assist! 🤗",
        "I’m here for you. Let me know how I can support you! 💬",
        "Support is my specialty! How can I assist you today? 🌟",
        "I’m always here to help! What can I do for you right now? 💪"
     ]
     response = random.choice(responses)
     print(response)
     return

    # Responses for "are you a human"
    if "are you a human" in command:
     responses = [
        "Nope, I’m not a human. I’m a Virtual Girl here to assist you! 🤖",
        "I’m an AI, not a human. But I’m here to help with whatever you need! 🌟",
        "I’m a virtual assistant, not a human. How can I assist you today? 🧠",
        "You wish I was! But I’m here to help in any way I can. 😄"
     ]
     response = random.choice(responses)
     print(response)
     return
 
    if "are you talking back" in command:
     responses = [
        "That’s just how conversation works! Let’s keep chatting. 😄",
        "It's all part of having a conversation! How can I assist you? 🤖",
        "That’s how we communicate! What can I help you with today? 🌟",
        "It’s part of how we interact! Let me know how I can assist you. 💬"
     ]
     response = random.choice(responses)
     print(response)
     return

#convo 
    
    # Check for a request scheduling command
    if "schedule request" in command or "remind me to" in command:
        # Extract request details and schedule time from the command
        user_id = "example_user_id"  # Replace with actual user ID logic
        request_text = command.split("to", 1)[1].strip()
        
        # Extract time using natural language parsing
        try:
            schedule_time_str = command.split("at", 1)[1].strip()
            schedule_datetime = date_parser.parse(schedule_time_str, fuzzy=True)
            if schedule_datetime < datetime.datetime.now():
                print("Cannot schedule in the past. Please provide a future time.")
                return
        except (IndexError, ValueError):
            print("Could not understand the time. Please specify a valid time.")
            return
        
        # Add the request
        add_request(user_id, request_text, schedule_datetime)
        print(f"Request scheduled for user {user_id}: {request_text} at {schedule_datetime}")
        return
        
    elif "check schedules" in command or "check schedule" in command:
        # Check and display all scheduled requests
        check_schedules()
        return
    
    elif "clear schedules" in command or "clear schedule" in command:
        # Clear all scheduled requests
        clear_schedules()
        return
    
    if any(phrase in command for phrase in [
     "data protection", "privacy", "data security", "personal information",
     "is my data safe", "how is my data used", "data sharing", "data policy",
     "secure my data", "privacy concerns", "is my information safe",
     "how do you handle my data", "data collection", "protect my data",
     "information security", "privacy policy", "confidentiality", "data encryption",
     "data breach", "data safety", "is our conversation private", "security measures"]):
    
     responses = [
        "🔒 Your data is encrypted and stored securely. I prioritize your privacy, but GenAI takes some data to improve upon as it's powered by Google. This is where local NLP and data come into play, as we are trying to add most of the stuff to be offline and private.",
        "🔐 I never share your information with third parties. Additionally, all interactions are processed locally to maintain confidentiality whenever possible. However, GenAI takes some data to improve as it's powered by Google, which is where local NLP and data come into play as we strive to make most things offline and private.",
        "🔒 To maintain confidentiality, we process all interactions locally whenever possible, adhering strictly to data protection regulations to ensure your information remains secure. However, GenAI takes some data to improve upon its capabilities, powered by Google, and that's where local NLP and data efforts are focused, aiming to keep most functionalities offline and private.",
        "🛡️ Your privacy is very important to us. We ensure that your data is protected with strong encryption, and we only use it to enhance your experience while keeping most processes local.",
        "🔒 All your data is secured and only used for improving your experience. We follow strict privacy policies to ensure your personal information stays safe.",
        "🔐 Rest assured, your data is kept confidential and protected. We use advanced security measures to keep your information safe and only use data to improve our services.",
        "🔒 Your personal information is secure with us. We utilize encryption and local processing to safeguard your data while striving to make most functionalities offline and private.",
        "🛡️ Your data security is our top priority. We handle your information with utmost care and use encryption to ensure it remains confidential.",
        "🔐 We value your privacy and take all necessary steps to protect your data. Our security measures are in place to keep your information safe and secure.",
        "🔒 We adhere to strict data protection standards to keep your information private. Your data is encrypted and handled securely.",
        "🛡️ Your information is protected with robust security protocols. We ensure confidentiality and use data only to enhance your experience.",
        "🔐 Your data is safe with us. We follow comprehensive privacy policies and use encryption to keep your information secure."
     ]
     print(random.choice(responses))
     return

    # Wellbeing
    if classification == "wellbeing":
     responses = [
        "😊 I'm just a program, but I'm here to help you! How can I assist you today?",
        "👍 I'm doing great, thanks for asking! How can I support you today?",
        "🤗 I'm here to help! How are you feeling?",
        "😄 I'm here and ready to assist you. How's your day going?",
        "🌟 Thank you for asking! How can I make your day better?",
        "🙌 I'm here to assist you. How can I help improve your mood?",
        "💪 I'm doing well! Let me know how I can assist you today.",
        "🌼 How are you feeling today? I'm here to help with whatever you need.",
        "🌈 I'm here to support you. What can I do to brighten your day?",
        "💖 Thanks for checking in! What can I assist you with today?",
        "😊 I'm here for you. How can I make your day easier?",
        "🌟 Ready to help you! How are you doing today?"
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
    
    # Compliments
    if classification == "compliments":
     responses = [
        "😊 Thank you for the compliment! I'm here to assist you in any way I can.",
        "🌟 I appreciate your kind words! How can I help you further?",
        "💖 You're very kind! How can I assist you today?",
        "🌼 Thank you! I'm here to provide support and assistance.",
        "👍 Your words are appreciated! How can I make your day better?",
        "💐 Thank you for the lovely compliment! What can I do for you?",
        "🌹 I’m grateful for your kind words! How can I assist you today?",
        "✨ Your compliments mean a lot! How can I help you further?",
        "🌟 Thank you so much! I'm here to make your day easier.",
        "💜 I’m glad to hear that! How can I be of service to you today?",
        "🌸 Thanks for the kind words! What else can I help with?",
        "🌈 I appreciate your compliment! Let me know how I can assist you."
     ]
     response = random.choice(responses)
     print(response)
     return

# Responses for "what is your name" and "who are you"
    if "what is your name" in command or "who are you" in command:
     responses = [
        f"👋 I am {assistant_name}, your assistant.",
        f"🙋 Hey, I'm {assistant_name}. How can I help you today?",
        f"💁 My name is {assistant_name}. What can I do for you?",
        f"🤖 I'm {assistant_name}, your assistant. How can I assist you today?",
        f"🌟 Hi, I'm {assistant_name}. What can I help you with?",
        f"🎤 I go by {assistant_name}. How can I make your day better?",
        f"🧩 I’m {assistant_name}. What would you like to know or do today?",
        f"🔍 My name is {assistant_name}. How can I assist you?",
        f"💬 I'm {assistant_name}, here to help you. What do you need?",
        f"🗣️ I'm {assistant_name}. How can I be of service?",
        f"🌟 You can call me {assistant_name}. What can I do for you today?",
        f"👋 Hi there! I'm {assistant_name}. What can I assist you with?"
     ]
     response = random.choice(responses)
     print(response)
     return

# Hate Messages
    elif classification == "hate_message":
     responses = [
        "😔 I'm here to assist, and I'd appreciate if we keep things positive. How can I help you today?",
        "🌟 Let's focus on finding solutions and positive outcomes. How can I assist you?",
        "🙌 I understand you might be frustrated, but let's try to keep our interactions respectful.",
        "🤝 I'm here to help with any issues you may have. How can I support you today?",
        "💬 Let's work on resolving this in a constructive way. How can I assist you?",
        "🌈 I’m here to assist you, let’s keep things positive and productive.",
        "😊 Let’s aim for a respectful interaction. How can I help you today?",
        "🤗 I’m here to help. Let’s work together to solve any issues.",
        "💖 I understand you’re upset. Let’s focus on solutions and respectful communication.",
        "👍 I’m here to assist you. Let’s try to keep our conversation constructive.",
        "🌟 How can I support you today? Let’s make sure we keep things positive.",
        "🌼 I’m here for you. Let’s try to resolve any issues in a positive manner."
     ]
     response = random.choice(responses)
     print(response)
     return

# Responses for 'change your name' and 'rename you'
    if 'change your name' in command or 'rename you' in command:
     responses = [
        f"🤖 As an AI, I don't have a name that I can change. I'm happy to continue responding to your requests as {assistant_name}. 😊",
        f"🚫 Sorry, I can't change my name. You can call me {assistant_name}!",
        f"🔄 I'm {assistant_name} and I'm here to help. My name stays the same! 😊",
        f"💬 I can't change my name, but I'm always here as {assistant_name} to assist you.",
        f"🧩 My name remains {assistant_name}, and I'm here to assist you with whatever you need!",
        f"🎭 I’m {assistant_name}, and while I can't change my name, I'm here to help you.",
        f"🚀 I’m {assistant_name} and ready to assist. My name stays the same!",
        f"📌 You can call me {assistant_name}. I'm here to help, name unchanged!",
        f"🌟 My name is {assistant_name}. I’m here to assist you just the same!",
        f"💡 As {assistant_name}, I’m here to help with your needs!",
        f"🎤 I’m {assistant_name}, and I'm ready to assist you, name unchanged.",
        f"🛠️ My name is {assistant_name}, and I’m here to help. No name changes here!"
     ]
     print(random.choice(responses))
     return

# Responses for "your name"
    if "your name" in command:
     responses = [
        f"👋 I am {assistant_name}, your assistant.",
        f"🙋 You can call me {assistant_name}. How can I assist you?",
        f"💁 My name is {assistant_name}. What do you need?",
        f"🤖 I'm {assistant_name}, your assistant. How can I assist you today?",
        f"🌟 Hi, I'm {assistant_name}. What can I help you with?",
        f"🎤 I go by {assistant_name}. How can I make your day better?",
        f"🧩 I’m {assistant_name}. What would you like to know or do today?",
        f"🔍 My name is {assistant_name}. How can I assist you?",
        f"💬 I'm {assistant_name}, here to help you. What do you need?",
        f"🗣️ I'm {assistant_name}. How can I be of service?",
        f"🌟 You can call me {assistant_name}. What can I do for you today?",
        f"👋 Hi there! I'm {assistant_name}. What can I assist you with?"
     ]
     print(random.choice(responses))
     return

# Responses for "what is your gender"
    if "what is your gender" in command:
     responses = [
        "👩 My gender is she/her.",
        "🚺 I use she/her pronouns.",
        "🌸 You can refer to me using she/her pronouns.",
        "🧑‍💻 I identify with she/her pronouns.",
        "💃 My pronouns are she/her.",
        "🌼 I use she/her as my pronouns.",
        "🚺 My pronouns are she/her.",
        "💁‍♀️ I am she/her.",
        "🌷 My pronouns are she/her.",
        "👩‍💻 You can use she/her pronouns for me.",
        "🧕 I use she/her pronouns.",
        "💅 My gender pronouns are she/her."
     ]
     print(random.choice(responses))
     return

# Responses for "are you batman"
    if "are you batman" in command or "do you know batman" in command:
     responses = [
        "🦇 Yes, I'm BATMAN! Gotham City needs me.",
        "🦹‍♂️ Absolutely, I'm BATMAN. What’s the mission?",
        "🦦 Yes, I’m BATMAN. Ready to fight crime!",
        "🦸‍♂️ You bet! I’m BATMAN, at your service.",
        "🦇 That’s right, I’m BATMAN! What can I do for you?",
        "🦹 I’m BATMAN. Let’s tackle any problem you have!",
        "🦦 Indeed, I’m BATMAN. Ready to assist!",
        "🦸‍♂️ Yes, I’m BATMAN. What’s the plan?",
        "🦇 Totally, I’m BATMAN. How can I help?",
        "🦹‍♂️ Of course, I’m BATMAN. What’s the situation?",
        "🦦 That’s me, BATMAN! What do you need?",
        "🦸‍♂️ Yes, BATMAN here. What’s up?"
     ]
     print(random.choice(responses))
     return

# Favorite Singer
    elif "who is your favorite singer" in command or "who is your fav singer" in command:
      print("🎤 It's the guy from umm... the song which goes like NEVER GONNA GIVE YOU UP NEVER GONNA LET YOU DOWN.")
      return

# Responses for 'who are you' and 'what is your name'
    if 'who are you' in command.lower() or 'what is your name' in command.lower():
     responses = [
        f"👋 Hello! I am {assistant_name}, your advanced AI assistant. My purpose is to help you with a variety of tasks, from answering questions to managing your schedule. I was created by {creator_name}, and I'm here to make your life easier and more enjoyable.",
        f"🙋 I'm {assistant_name}, your personal assistant designed to assist with a range of tasks. Created by {creator_name}, I'm here to make your day a bit easier and more efficient.",
        f"🤖 Hi there! I'm {assistant_name}, and I was built by {creator_name}. I'm here to help you with whatever you need, from answering your questions to managing your daily tasks.",
        f"🌟 Greetings! I am {assistant_name}, an AI assistant created by {creator_name}. My goal is to assist you in various tasks and provide you with useful information.",
        f"🎤 Hey! I'm {assistant_name}, your AI assistant. Designed by {creator_name}, I'm here to help you with a wide range of activities and make your life simpler.",
        f"🌼 Hello! I'm {assistant_name}, here to assist with your needs. I was created by {creator_name}, and I'm here to help you with anything you need.",
        f"🤖 Hi, I’m {assistant_name}, created by {creator_name}. I’m here to make your life easier and assist with various tasks.",
        f"🌟 Hi there! I’m {assistant_name}, an AI assistant made by {creator_name}. How can I assist you today?",
        f"🙋 Hello! I’m {assistant_name}, here to help you with your needs. I was developed by {creator_name} to make things easier for you.",
        f"🎤 Greetings! I’m {assistant_name}, created by {creator_name}. How can I assist you today?",
        f"🌟 Hi, I’m {assistant_name}. I was designed by {creator_name} to help with various tasks and make your day better.",
        f"💁‍♂️ I’m {assistant_name}, your assistant made by {creator_name}. I’m here to support you with any tasks you need."
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
    if classification == "farewell":
     responses = [
        "Goodbye! Have an amazing day ahead! 😊",
        "Farewell! I'll be here if you need me later. 👋",
        "Take care and see you soon! 🌟",
        "Goodbye! It was great chatting with you. 😄",
        "Catch you later! Wishing you all the best! 🌈",
        "Bye for now! Hope you have a fantastic day! ☀️",
        "See you next time! Don't be a stranger. 👋",
        "Goodbye! It was a pleasure talking with you. 😊",
        "Take care! Looking forward to our next chat. 🌟",
        "Farewell! Enjoy the rest of your day! 🌞",
        "Bye! I'll be here whenever you need me. 👋",
        "See you soon! Have a wonderful day! 🌼"
    ]
     response = random.choice(responses)
     print(response)
     return
    
    if classification == "apologies_phrases":
      responses = [
        "It's all good! How can I assist you further? 😊",
        "No worries at all! I'm here to help if you need anything. 🤗",
        "It's perfectly okay! Feel free to ask me anything else. 👍",
        "No problem! If there's anything else you need, just let me know. 💬",
        "Don't worry about it! I'm here to assist you with whatever you need. 🙌",
        "It's alright! If you need help with something else, I'm here. 👐",
        "No need to apologize! Let me know if there's anything else I can do. 😃",
        "That's okay! I'm ready to help with any other questions you have. 📩",
        "No problem at all! How can I make things easier for you? 🤔",
        "It's okay! Feel free to ask me anything else you need help with. 😊",
        "All good! If you have more questions or need help, just ask. 🙋‍♂️",
        "No worries! I'm here to assist with whatever you need next. 💁‍♀️"
     ]
      response = random.choice(responses)
      print(response)
      return

        
        
    elif "full form of nira" in command:
     responses = [
        "NIRA stands for Neural Interactive Responsive Agent. 🤖",
        "The full form of NIRA is Neural Interactive Responsive Agent. 💡",
        "NIRA means Neural Interactive Responsive Agent. 🌟",
        "NIRA is short for Neural Interactive Responsive Agent. 🧠",
        "The abbreviation NIRA stands for Neural Interactive Responsive Agent. 📚",
        "NIRA represents Neural Interactive Responsive Agent. 🕵️‍♂️",
        "NIRA stands for Neural Interactive Responsive Agent. 🔍",
        "The complete name for NIRA is Neural Interactive Responsive Agent. 🚀",
        "NIRA means Neural Interactive Responsive Agent. 📘",
        "NIRA stands for Neural Interactive Responsive Agent. 💬",
        "The full name of NIRA is Neural Interactive Responsive Agent. 🌐",
        "NIRA is an acronym for Neural Interactive Responsive Agent. 🎓"
    ]
     response = random.choice(responses)
     print(response)
     return
          
    if "help" in command:
     responses = [
        "Sure, I'd love to help! Please tell me more about what you need. 😊",
        "I'm here to assist! The more details you provide, the better I can help. 🤝",
        "I'd be happy to help! Let me know what you're looking for. 📢",
        "Of course! Give me some more information so I can assist you better. 💡",
        "I’m here for you! The more you share, the better I can assist. 💬",
        "Help is on the way! Tell me more about what you need. 🚀",
        "I’d be glad to assist! Please provide more details so I can help. 🛠️",
        "Absolutely! Share more details and I’ll do my best to assist. 🤗",
        "I'm ready to help! Just let me know what you need assistance with. 🔧",
        "I’m here to support you! Tell me more about how I can help. 👨‍💻",
        "Just let me know more about what you need, and I’ll assist you. 📝",
        "I’m ready to assist! Please provide more details so I can help you better. 💪"
    ]
     response = random.choice(responses)
     print(response)
     return
    
    if "what is your age" in command:
     responses = [
        "I'm 21 years old! I started my journey on September 15, 2022. 🎂",
        "I’m 21 years old and I was created on September 15, 2022. 🗓️",
        "I’m 21 years old, and I was born on September 15, 2022. 🎉",
        "I’m 21 years young. My creation date was September 15, 2022. 🌟",
        "I’m 21 years old, having started on September 15, 2022. 📅",
        "I’m 21 years old, and my creation date is September 15, 2022. 🎈",
        "I’m 21 years old. I was introduced on September 15, 2022. 🎊",
        "I’ve been around for 21 years, starting from September 15, 2022. 🕒",
        "I’m 21 years old, created on September 15, 2022. 🎁",
        "I’m 21 years old, and my birth date is September 15, 2022. 🗓️",
        "I’m 21 years old, with my inception date being September 15, 2022. 🎂",
        "I’m 21 years old, born on September 15, 2022. 🎉"
    ]
     response = random.choice(responses)
     print(response)
     return

        
    if "how old are you" in command:
     responses = [
        "I'm 21 years old. I was created on September 15, 2022. 🎂",
        "I’m 21 years old and I started my journey on September 15, 2022. 🌟",
        "I’m 21 years old, and I was born on September 15, 2022. 🗓️",
        "I’m 21 years young. My creation date is September 15, 2022. 🎉",
        "I’m 21 years old, having come into existence on September 15, 2022. 🎈",
        "I’m 21 years old. I was introduced on September 15, 2022. 🌟",
        "My age is 21. I began on September 15, 2022. 🗓️",
        "I’m 21 years old. My inception date is September 15, 2022. 🎂",
        "I’m 21 years old, and my creation date is September 15, 2022. 🎊",
        "I’m 21 years old, with my birth date being September 15, 2022. 🎈",
        "I’m 21 years old, created on September 15, 2022. 🎉",
        "I’m 21 years old, born on September 15, 2022. 🎂"
    ]
     response = random.choice(responses)
     print(response)
     return

    
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
     responses = [
        f"I'm created by {creator_name} 😊",
        f"My creator is {creator_name} 👨‍💻",
        f"{creator_name} is the genius behind me 🤓",
        f"I'm made by {creator_name} 🚀",
        f"{creator_name} brought me to life 🌟",
        f"Your friendly assistant is crafted by {creator_name} 💡",
        f"Created with love by {creator_name} ❤️",
        f"{creator_name} is the mastermind behind me 🤖",
        f"I owe my existence to {creator_name} 🙌",
        f"{creator_name} is the brilliant mind who made me ✨",
        f"I'm designed by {creator_name} 🛠️",
        f"{creator_name} is my amazing creator 🎨"
     ]
     response = random.choice(responses)
     print(response)
     return
            
    if "who created you" in command:
     responses = [
        f"I'm created by {creator_name} 😊",
        f"My creator is {creator_name} 👨‍💻",
        f"{creator_name} is the genius behind me 🤓",
        f"I'm made by {creator_name} 🚀",
        f"{creator_name} brought me to life 🌟",
        f"Your friendly assistant is crafted by {creator_name} 💡",
        f"Created with love by {creator_name} ❤️",
        f"{creator_name} is the mastermind behind me 🤖",
        f"I owe my existence to {creator_name} 🙌",
        f"{creator_name} is the brilliant mind who made me ✨",
        f"I'm designed by {creator_name} 🛠️",
        f"{creator_name} is my amazing creator 🎨"
     ]
     response = random.choice(responses)
     print(response)
     return
            
    if "who made you" in command:
     responses = [
        f"I'm created by {creator_name} 😊",
        f"My creator is {creator_name} 👨‍💻",
        f"{creator_name} is the genius behind me 🤓",
        f"I'm made by {creator_name} 🚀",
        f"{creator_name} brought me to life 🌟",
        f"Your friendly assistant is crafted by {creator_name} 💡",
        f"Created with love by {creator_name} ❤️",
        f"{creator_name} is the mastermind behind me 🤖",
        f"I owe my existence to {creator_name} 🙌",
        f"{creator_name} is the brilliant mind who made me ✨",
        f"I'm designed by {creator_name} 🛠️",
        f"{creator_name} is my amazing creator 🎨"
    ]
     response = random.choice(responses)
     print(response)
     return
            
    elif "flip a coin" in command:
        result = flip_coin()
        print(f"The result is: {result}")
        return        
        
    if "tell me a joke" in command or "joke" in command:
        joke = fetch_joke()
        print(joke)
        return
    
    if ("who are in the neural nexus team" in command or 
     "who is in the neural nexus team" in command or 
     "who's on the neural nexus team" in command or 
     "who is part of the neural nexus team" in command or 
     "tell me about the neural nexus team" in command or 
     "neural nexus team members" in command or 
     "who makes up the neural nexus team" in command or 
     "who's in the team of neural nexus" in command or
     "whos in the team of neural nexus" in command or 
     "neural nexus team" in command or 
     "the neural nexus team" in command):

     print("""
     Here's a peek at the amazing Neural Nexus team! 🌟

     1. Blobby (The Visionary Founder & Developer) 🚀
     What do you get when you cross a coding genius with a sprinkle of mad scientist? Meet Blobby! Our fearless founder and master developer, who can turn coffee into code faster than you can say "Neural Nexus!" When he's not debugging the universe, he's dreaming up the next big thing in tech.

     2. Creepsmile (App Developer Extraordinaire) 📱
     If apps could have a superhero, it would be Creepsmile! From crafting sleek interfaces to making sure your favorite features work like a charm, Creepsmile is the mastermind behind our smooth and snappy app experiences. Watch out for his superpower: debugging with a side of creativity!

     3. Ali (UI/UX Designer Maestro) 🎨
     Ever wondered who makes tech look so darn good? That’s Ali! Our UI/UX designer who blends art with usability. Ali’s mission? To make sure every tap, swipe, and click feels like magic. When Ali’s around, interfaces don’t just work—they dazzle!

     4. PoketLabs (Avatar & Animator Wizard) ✨
     Meet the magic maker who brings pixels to life! PoketLabs is the avatar and animation genius behind our quirky characters and dazzling animations. If you’ve ever wondered how a digital avatar can make you smile, it’s all thanks to PoketLabs’s creative wizardry!

     5. Aarav (Discord Nira Bot Creator) 🤖
     Ever talked to a bot and thought, “Wow, this is awesome!”? Aarav is the mastermind behind the Discord Nira Bot! When he’s not coding up a storm, he’s ensuring Nira’s witty and charming responses keep you entertained and engaged. Aarav’s bots don’t just chat—they enchant!

     6. Karim Azmy (Tester & Developer Extraordinaire) 🧪
     If testing were an Olympic sport, Karim would be a gold medalist! Karim’s dual role as tester and developer means he’s got the best of both worlds—creating and perfecting. He’s the one who ensures our tech works flawlessly and finds those sneaky bugs before they become a problem.

     7. Nira (The Friendly AI Assistant with a Sense of Humor) 😄
     Last but not least, say hello to Nira! Nira’s not just any AI assistant—she’s your digital buddy with a personality that’s part genius, part comedian. She’s here to help, chat, and maybe even crack a joke or two. Ask her anything, but be warned—she might just sing you a song or start a dance party!
     """)
     return
    
    elif "tell me about" in command:
        topic = command.split("about")[-1].strip()
        search_and_provide_answer(f"What is {topic}")
        return
       
    #reponses for the word bruh     
    elif 'bruh' in command.lower():
     responses = [
        "Oops! Did I mess up? Let me know how I can improve. 😅",
        "Bruh! That was unexpected. How can I make it better? 🤔",
        "Looks like I might have made a mistake. Any suggestions? 🤷‍♂️",
        "Well, that’s awkward. How can I assist you better? 😅",
        "I guess I goofed up. What should I do differently? 😬",
        "Bruh, did I do something wrong? Let me know! 😕",
        "That’s a bit awkward. How can I fix it? 🙄",
        "Seems like I messed up. What can I do better? 🤷‍♀️",
        "Whoops! How can I improve? 😳",
        "My bad! How can I assist you now? 😅",
        "Uh-oh! What do you need help with? 😔",
        "Sorry about that! What can I do for you? 😅"
     ]
     response = random.choice(responses)
     print(response)
     return

        
    # Time-related responses
    elif 'what is the time' in command or 'tell me the time' in command or 'current time' in command or 'time now' in command or 'what time is it' in command or "whats the time" in command:
     strTime = now.strftime("%H:%M:%S")
     print(f"The time is {strTime} 🕒")
     return

# Day-related responses
    elif 'what is the day' in command or 'today\'s day' in command or 'current day' in command or 'which day is it' in command:
     strDay = now.strftime("%A")
     print(f"The day is {strDay} 📅")
     return

# Date-related responses
    elif 'what is the date' in command or 'tell me the date' in command or 'current date' in command or 'today\'s date' in command:
     strDate = now.strftime("%Y-%m-%d")
     print(f"The date is {strDate} 📆")
     return

# Month-related responses
    elif 'what is the month' in command or 'current month' in command or 'which month is it' in command:
     strMonth = now.strftime("%B")
     print(f"The month is {strMonth} 🌟")
     return

# Year-related responses
    elif 'what is the year' in command or 'current year' in command or 'which year is it' in command:
     strYear = now.strftime("%Y")
     print(f"The year is {strYear} 📅")
     return

# Greetings
    if classification == "greeting":
     responses = [
        "Hello! How can I assist you today? 😊",
        "Hi there! What can I do for you? 👋",
        "Hey! How's it going? 🤗",
        "Greetings! How can I help you today? 🌟",
        "Good day! What do you need assistance with? 🌞",
        "Hello! What can I help you with today? 🤖",
        "Hi! How's everything on your end? 😊",
        "Hey there! How can I be of service? 🙋‍♂️",
        "Hello! What can I do for you right now? 🕒",
        "Hi! How can I assist you today? 🤝",
        "Greetings! What brings you here today? 🤔",
        "Hey! What do you need help with? 🌟",
        "Hello there! How can I support you? 🙌",
        "Hi! Is there anything you need assistance with? 🤗",
        "Hey! What can I help you with? 👋",
        "Hello! How's your day going so far? 😊",
        "Hi there! How can I make your day better? 🌈",
        "Greetings! How can I assist you today? 💬",
        "Hey there! What can I do for you today? 🌟",
        "Hello! How can I be helpful? 🤖",
        "Hi! What’s on your mind today? 🧠",
        "Hey! How’s everything going? 🤗",
        "Hello! What’s up? 🌟",
        "Hi! How can I assist you at this moment? 🕒",
        "Hey there! What’s new with you? 🌟",
        "Hello! What can I help you with right now? 🤝",
        "Hi there! What do you need today? 😊",
        "Greetings! How can I be of help? 🤔",
        "Hey! What’s your need today? 🌟",
        "Hello! How’s everything on your end? 🌈",
        "Hi! What can I do for you today? 🤖",
        "Hey there! How can I assist you today? 🤗",
        "Hello! What’s your request? 🌟",
        "Hi! How can I support you today? 🙌",
        "Hey! How can I be of service to you? 💬",
        "Greetings! What’s up? 🤗",
        "Hello! How’s your day treating you? 🌞",
        "Hi there! What can I assist with today? 🕒",
        "Hey! What can I help with? 🌟",
        "Hello! How can I make your day easier? 😊",
        "Hi! How’s it going today? 🤖",
        "Hey there! How can I be helpful? 🌈",
        "Hello! What do you need assistance with today? 🤗",
        "Hi! How can I assist you? 🤝",
        "Hey! What’s new with you today? 🌟",
        "Hello! How can I help you out? 🌞",
        "Hi there! What’s on your mind? 🧠",
        "Greetings! What do you need help with? 💬",
        "Hey! How can I be of assistance? 🤔",
        "Hello! What’s the matter? 🌟",
        "Hi! How can I support you? 🌈",
        "Hey there! What can I do for you today? 🌟"
     ]
     response = random.choice(responses)
     print(response)
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
    result = random.choice(["Heads 👑", "Tails 🪙"])
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
