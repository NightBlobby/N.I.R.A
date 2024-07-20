import tkinter as tk
from tkinter import messagebox, scrolledtext
import webbrowser
import speech_recognition as sr
import pyttsx3
import threading
import datetime
import requests
import random
import smtplib
from email.message import EmailMessage
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from translate import Translator
from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
import pyowm

# Download NLTK resources if not already downloaded
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('stopwords')

# Initialize speech recognition and text-to-speech engines
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# Function to speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's command
def listen():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return None
    except Exception as e:
        speak(f"An error occurred: {e}")
        return None

# Initialize translator
translator = Translator(to_lang='en')

# Function to translate text
def translate_text(text, dest_lang):
    try:
        translation = translator.translate(text, dest_lang)
        return translation
    except Exception as e:
        return f"Translation failed: {e}"

# Initialize currency converter
currency_converter = CurrencyRates()
btc_converter = BtcConverter()

# Initialize weather API with your API key
owm = pyowm.OWM('YOUR_API')  # Replace with your OpenWeatherMap API key

# Function to fetch weather information for a given city
def get_weather(city_name):
    try:
        observation = owm.weather_manager().weather_at_place(city_name)
        weather = observation.weather
        temperature = weather.temperature('celsius')['temp']
        status = weather.detailed_status
        return city_name, temperature, status
    except Exception as e:
        return None, None, f"Error: {e}"

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

# Function to greet the user
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good morning!")
    elif hour < 18:
        speak("Good afternoon!")
    else:
        speak("Good evening!")
    now = datetime.datetime.now()
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}, and the time is {now.strftime('%I:%M %p')}.")

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
        api_key = "YOU_API"  # Replace with your API key
        search_engine_id = "YOUR_API"  # Replace with your search engine ID
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

# Function to classify sentence as command or question
def classify_sentence(sentence):
    tokens = word_tokenize(sentence)
    words = [word for word in tokens if word.isalnum()]
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.lower() not in stop_words]
    tagged_words = nltk.pos_tag(words)
    question_words = ['WDT', 'WP', 'WP$', 'WRB']
    for word, tag in tagged_words:
        if tag in question_words:
            return "question"
    return "command"

# Memory storage dictionary
memory = {}

# Function to remember information
def remember(key, value):
    memory[key] = value
    speak(f"I will remember {key} as {value}.")

# Function to retrieve remembered information
def retrieve_memory(key):
    if key in memory:
        return memory[key]
    else:
        return "I don't remember anything about that."

# Function to parse and execute the user command
def parse_and_execute_command(command):
    # Standardize the command to lower case
    command = command.lower()

    # Lists of phrases to match against
    compliments = ["you are beautiful", "you are smart", "you are awesome", "you're beautiful"]
    thanks = ["thanks", "thank you", "thank"]
    goodbye = ["goodbye", "bye", "exit"]

    classification = classify_sentence(command)
    if classification == "question":
        search_and_provide_answer(command)
        return
    
    if any(compliment in command for compliment in compliments):
        speak("Thank you!")
    elif any(thank in command for thank in thanks):
        speak("You're welcome.")
    elif any(exit_command in command for exit_command in goodbye):
        speak("Goodbye and take care!")
        exit()
    elif "what is your name" in command or "who are you" in command:
        speak("I am your personal assistant.")
    elif "calculate" in command:
        try:
            # Extract the mathematical expression
            expression = command.split("calculate")[1].strip()
            # Evaluate the expression
            result = eval(expression)
            speak(f"The result of {expression} is {result}")
        except Exception as e:
            speak(f"Sorry, I couldn't calculate that. Error: {e}")
        return
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
            parts = info.split("as")
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                remember(key, value)
            else:
                speak("Sorry, I didn't catch that. Please say 'remember [key] as [value]'.")
        else:
            speak("Sorry, I didn't catch that. Please say 'remember [key] as [value]'.")
    elif "recall" in command or "retrieve" in command:
        tokens = command.split("recall") if "recall" in command else command.split("retrieve")
        if len(tokens) > 1:
            key = tokens[1].strip()
            info = retrieve_memory(key)
            speak(info)
        else:
            speak("Sorry, I didn't catch that. Please specify what you want to recall.")
    elif "translate" in command:
        tokens = command.split("translate")
        if len(tokens) > 1:
            to_translate = tokens[1].strip()
            translated_text = translate_text(to_translate, 'en')
            speak(translated_text)
        else:
            speak("Sorry, I didn't catch that. Please say 'translate [text]' to translate.")
    elif "convert currency" in command:
        speak("Sure, please specify the amount and currencies to convert.")
        amount = None
        while not amount:
            amount_text = listen()
            try:
                amount = float(amount_text)
            except ValueError:
                speak("Sorry, I didn't catch that. Please specify the amount again.")

        speak("What currency would you like to convert from?")
        from_currency = listen()

        speak("What currency would you like to convert to?")
        to_currency = listen()

        try:
            result = currency_converter.convert(from_currency.upper(), to_currency.upper(), amount)
            speak(f"{amount} {from_currency.upper()} is approximately {result} {to_currency.upper()}.")
        except Exception as e:
            speak(f"Conversion failed. Error: {e}")
    elif "convert bitcoin" in command or "bitcoin" in command:
        speak("Sure, please specify the amount to convert.")
        amount = None
        while not amount:
            amount_text = listen()
            try:
                amount = float(amount_text)
            except ValueError:
                speak("Sorry, I didn't catch that. Please specify the amount again.")

        speak("What currency would you like to convert to?")
        to_currency = listen()

        try:
            result = btc_converter.convert_to_btc(amount, to_currency.upper())
            speak(f"{amount} BTC is approximately {result} {to_currency.upper()}.")
        except Exception as e:
            speak(f"Conversion failed. Error: {e}")
    else:
        search_and_provide_answer(command)
# Function to toggle between themes
def get_weather(city):
    api_key = '5a16d7f729e69aced4b2d8745c1d6f6c'
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    try:
        response = requests.get(base_url)
        weather_data = json.loads(response.text)
        city_name = weather_data['name']
        temperature = weather_data['main']['temp']
        status = weather_data['weather'][0]['description'].capitalize()
        return city_name, temperature, status
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return "Error", "--", "--"

# Function to toggle between themes
def toggle_theme():
    current_theme = root.cget('bg')
    if current_theme == "#1E1E1E":
        # Switch to Light theme
        new_theme = "#F5F5F5"  # Light Gray
        button_color = "#3F51B5"  # Indigo
        text_color = "#212121"  # Dark Text
        content_bg = "#FFFFFF"  # White
    else:
        # Switch to Dark theme
        new_theme = "#1E1E1E"  # Dark Gray
        button_color = "#2196F3"  # Blue
        text_color = "#FFFFFF"  # White
        content_bg = "#424242"  # Dark Background

    # Update root and frame colors
    root.configure(bg=new_theme)
    header_frame.configure(bg=new_theme)
    header_label.configure(bg=new_theme, fg=text_color)
    main_frame.configure(bg=content_bg)
    sidebar_frame.configure(bg=button_color)
    for widget in sidebar_frame.winfo_children():
        if isinstance(widget, tk.Button):
            widget.configure(bg=button_color, fg=text_color)
    command_history_text.configure(bg=content_bg, fg=text_color)
    footer_label.configure(bg=new_theme, fg=text_color)

# Function to greet the user
def greet_user():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greet = "Good morning!"
    elif 12 <= hour < 18:
        greet = "Good afternoon!"
    else:
        greet = "Good evening!"
    
    time_label.configure(text=datetime.datetime.now().strftime('%I:%M %p'))
    date_label.configure(text=datetime.datetime.now().strftime('%A, %B %d, %Y'))
    update_weather("New York")  # Default city

# Function to update weather information based on city input
def update_weather(city):
    city_name, temperature, status = get_weather(city)
    weather_label.configure(text=f"{city_name} | {temperature}°C | {get_weather_icon(status)} {status}")

# Function to get emoji based on weather status
def get_weather_icon(status):
    status = status.lower()
    if "clear" in status:
        return "☀️"
    elif "clouds" in status:
        return "☁️"
    elif "rain" in status:
        return "🌧️"
    elif "thunderstorm" in status:
        return "⛈️"
    elif "snow" in status:
        return "❄️"
    else:
        return ""

# Function to handle button clicks
def handle_button_click(button_text):
    if button_text == "Listen...":
        listen_command()
    elif button_text == "GitHub Page":
        open_github_page()
    elif button_text == "Help!":
        show_help()
    elif button_text == "Update Weather":
        city = city_entry.get()
        update_weather(city)

# Function to listen for voice input
def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"Recognized command: {command}")
        # Depending on the recognized command, you can trigger actions here
        # For example, process the command to fetch weather or perform other tasks
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

# Function to open GitHub page
def open_github_page():
    import webbrowser
    webbrowser.open_new("https://github.com/NightBlobby/N.A.I.N.A")

# Function to show help information
def show_help():
    help_text = "Commands you can try:\n" \
                "- Ask for weather: 'What is the weather in [city]?'\n" \
                "- Send email: 'Send an email'\n" \
                "- Set timer: 'Set a timer for [duration] seconds'\n" \
                "- Translate text: 'Translate [text]'\n" \
                "- Convert currency: 'Convert [amount] [currency] to [currency]'\n" \
                "- Convert Bitcoin: 'Convert Bitcoin'\n" \
                "- Tell me a joke: 'Tell me a joke'\n" \
                "- Open websites: 'Open YouTube', 'Open Google', 'Open Spotify', etc.\n" \
                "- Remember information: 'Remember [key] as [value]'\n" \
                "- Retrieve information: 'Recall [key]', 'Retrieve [key]'\n" \
                "- Exit the assistant: 'Goodbye', 'Exit'\n" \
                "- Get help: 'What can you do?', 'Help!'\n" \
                "- And more!"
    messagebox.showinfo("Help", help_text)

# Function to create the UI
def create_ui():
    global root, header_frame, header_label, main_frame, sidebar_frame, content_frame, footer_label, command_history_text, time_label, date_label, weather_label, city_entry

    root = tk.Tk()
    root.title("AI Assistant")
    root.geometry("800x600")
    root.configure(bg="#1E1E1E")  # Set default background color

    # Header
    header_frame = tk.Frame(root, bg="#1E1E1E", padx=10, pady=10)
    header_frame.pack(side=tk.TOP, fill=tk.X)

    header_label = tk.Label(header_frame, text="AI Assistant", font=("Arial", 24, "bold"), bg="#1E1E1E", fg="#FFFFFF")
    header_label.pack()

    # Time, Date, Day, and Weather widgets
    time_label = tk.Label(header_frame, font=("Arial", 14), bg="#1E1E1E", fg="#FFFFFF")
    time_label.pack()

    date_label = tk.Label(header_frame, font=("Arial", 14), bg="#1E1E1E", fg="#FFFFFF")
    date_label.pack()

    weather_label = tk.Label(header_frame, font=("Arial", 14), bg="#1E1E1E", fg="#FFFFFF")
    weather_label.pack()

    # Main content area
    main_frame = tk.Frame(root, bg="#FFFFFF")  # White
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Left sidebar
    sidebar_frame = tk.Frame(main_frame, bg="#1E1E1E")  # Match main background color
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

    nav_buttons = ["Listen...", "GitHub Page", "Help!"]  # Updated button text
    button_colors = ["#1976D2", "#FF5722", "#4CAF50"]  # Different colors for each button
    for i, button_text in enumerate(nav_buttons):
        button = tk.Button(sidebar_frame, text=button_text, font=("Arial", 14), bg=button_colors[i], fg="#FFFFFF", width=15, bd=0, highlightthickness=0, command=lambda b=button_text: handle_button_click(b))
        button.pack(pady=5, padx=10, fill=tk.X)

    # City entry and Update Weather button
    city_label = tk.Label(sidebar_frame, text="Enter City:", font=("Arial", 14), bg="#1E1E1E", fg="#FFFFFF")
    city_label.pack(pady=(20, 10))

    city_entry = tk.Entry(sidebar_frame, font=("Arial", 12))
    city_entry.pack(padx=10, pady=5, fill=tk.X)

    update_weather_button = tk.Button(sidebar_frame, text="Update Weather", font=("Arial", 14), bg="#2196F3", fg="#FFFFFF", width=15, bd=0, highlightthickness=0, command=lambda: handle_button_click("Update Weather"))
    update_weather_button.pack(pady=5, padx=10, fill=tk.X)

    # Main content area (right side)
    content_frame = tk.Frame(main_frame, bg="#FFFFFF")  # White
    content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Command history text box
    command_history_label = tk.Label(content_frame, text="Command History", font=("Arial", 16), bg="#FFFFFF", fg="#212121")  # Dark Text
    command_history_label.pack(pady=(20, 10))

    command_history_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=40, height=10, font=("Arial", 12), bg="#FFFFFF", fg="#212121")  # Dark Text
    command_history_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Footer
    footer_label = tk.Label(root, text="© 2024 NightBlobby. All rights reserved.", font=("Arial", 10), bg="#1E1E1E", fg="#FFFFFF", anchor="se", padx=10, pady=5)
    footer_label.pack(fill=tk.X, side=tk.BOTTOM)

    greet_user()  # Call greet_user to initialize time, date, day, and weather

    root.mainloop()

# Entry point of the program
if __name__ == "__main__":
    create_ui()
