# 🤖 NEURAL INTERACTIVE RESPONSIVE AGENT (N.I.R.A)

**NEURAL INTERACTIVE RESPONSIVE AGENT (N.I.R.A)** is an advanced AI assistant designed to integrate seamlessly into your daily routine. Built with Python, N.I.R.A. leverages cutting-edge technology to offer a comprehensive suite of features while adhering to strict privacy and security standards. Our vision is to evolve N.I.R.A into a sophisticated app available on the Play Store, providing a personalized and secure assistant experience.

---

## 📚 Table of Contents

- 🌟 [Key Features](#-key-features)
- 🛠️ [Installation and Prerequisites](#-installation-and-prerequisites)
- 🔧 [How It Works](#-how-it-works)
- 🚧 [Roadmap](#-roadmap)
- 🤝 [Contributing](#-contributing)
- 🦺 [Support](#-support)
- 📬 [Contact](#-contact)

---

## 🌟 Key Features

- **Privacy-First Approach**: Operates entirely locally with no external data sharing or retention.
- **Advanced AI Capabilities**: Provides intelligent, context-aware responses and actions.
- **Voice Recognition**: Processes and understands commands through sophisticated speech recognition.
- **Text-to-Speech**: Converts text to speech using `pyttsx3` for natural and clear communication.
- **Weather Information**: Retrieves real-time weather data via the OpenWeatherMap API.
- **Joke Fetching**: Delivers jokes through an integrated online API for user engagement.
- **Timer and Alarm Management**: Allows users to set, manage, and customize timers and alarms.
- **Google Custom Search**: Conducts and presents search results using the Google Custom Search API.
- **Natural Language Processing (NLP)**: Utilizes `nltk` and `sklearn` for advanced NLP and intent classification.
- **Bluetooth and NFC Scanning**: Identifies and interacts with nearby Bluetooth and NFC devices.
- **Dictionary and Thesaurus**: Provides word definitions and synonyms through `PyDictionary`.
- **Currency Conversion**: Converts currencies using `forex-python` for financial management.
- **News Retrieval**: Fetches top news headlines via the NewsAPI.
- **End-to-End Encryption**: Secures all communications to maintain user privacy.

---

## 🛠️ Installation and Prerequisites

### Prerequisites

- **Python 3.7+**: Ensure Python 3.7 or later is installed on your system.
- **Required Libraries**: Install the necessary libraries using the provided `requirements.txt` file.

### Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/N.I.R.A.git
    cd N.I.R.A
    ```

2. **Create a Virtual Environment (Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configuration**

    - **API Keys**: Obtain and configure API keys for Google Custom Search, OpenWeatherMap, NewsAPI, etc.
    - **Configuration File**: Create a `.env` file in the root directory and add your API keys and other settings.

---

## 🛠️ How It Works

### Voice Recognition

Utilizes the `speech_recognition` library to process spoken commands. The system captures audio input, converts it to text, and executes the corresponding action.

### Text-to-Speech

The `pyttsx3` library is used to convert text responses into spoken words, enabling natural and clear communication.

### Weather Information

Fetches weather details for a specified location using the OpenWeatherMap API. Users can request current weather conditions and forecasts.

### Joke Fetching

Integrates with an online joke API to provide random jokes for user entertainment and engagement.

### Timer and Alarm

Users can set and manage timers and alarms, with options for customizing alert sounds and durations.

### Google Custom Search

Performs search queries and retrieves results using the Google Custom Search API. This feature allows users to obtain information from the web directly.

### Natural Language Processing (NLP)

Employs `nltk` and `sklearn` for processing natural language and classifying user intents, enabling sophisticated understanding and responses.

### Bluetooth and NFC Scanning

Scans for and identifies nearby Bluetooth and NFC devices. This feature helps in interacting with various smart devices.

### Dictionary Lookup

Provides definitions, synonyms, and usage examples for words using `PyDictionary`.

### Currency Conversion

Converts amounts between different currencies using the `forex-python` library, assisting users in financial transactions.

### News Retrieval

Retrieves top news headlines from various sources using the NewsAPI, keeping users updated with current events.

### Convertations

Added the ability to have a decent conversation with the AI.

### Computer Vision

It can understand what its seeing and help u either find info about the object or help you solve the problem (still unter deverlopment it has a lot of errors)

### Rock Paper Scissors

you can play rock paper scissors with the AI!

### Coin Flip

You can make Coin flips idk i just felt it would be fun igs

### Greetings

It will greet you everytime you run it giving you all the info you need like time and date

### End-to-End Encryption

Ensures all data transmissions are encrypted, maintaining user privacy and security.

---

## 🚧 Roadmap

- **Expand Platform Support**: Add compatibility for additional operating systems including macOS and Linux.
- **Enhance AI Capabilities**: Improve AI-driven responses and contextual understanding.
- **Mobile App Development**: Develop and release a user-friendly mobile app.
- **Feature Expansion**: Incorporate user-requested features and improvements.
- **User Experience Enhancements**: Refine UI/UX based on user feedback.

---

## 🤝 Contributing

We welcome contributions from the community to improve N.I.R.A. Here’s how you can help:

1. **Fork the Repository**: Create your own fork of the repository on GitHub.
2. **Create a New Branch**: Develop your changes on a separate branch.
3. **Implement Your Changes**: Make your modifications and ensure they are thoroughly tested.
4. **Submit a Pull Request**: Open a pull request with a detailed description of your changes.

For detailed guidelines, please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## 🦺 Support

If you encounter issues or need assistance, please reach out via Discord: **[@nightblobby](https://discord.com/@me/nightblobby)**

---

## 📬 Contact

For questions, feedback, or collaboration opportunities, contact me on Discord: **[@nightblobby](https://discord.com/@me/nightblobby)**

---

