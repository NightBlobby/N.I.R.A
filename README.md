# 🤖 NEURAL INTERACTIVE RESPONSIVE AGENT (N.I.R.A)

**NEURAL INTERACTIVE RESPONSIVE AGENT (N.I.R.A)** represents a sophisticated AI assistant built to seamlessly integrate into your daily life. Developed in Python, N.I.R.A combines advanced technology with stringent privacy and security measures. Our goal is to evolve N.I.R.A into a top-tier app available on the Play Store, delivering a tailored and secure assistant experience.

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

- **Privacy-Centric Design**: Operates entirely locally, ensuring no external data sharing or retention.
- **Advanced AI Capabilities**: Delivers intelligent, context-aware responses and actions.
- **Voice Recognition**: Utilizes sophisticated speech recognition to understand and process commands.
- **Flexible Input**: Accepts both voice and text commands.
- **Text-to-Speech**: Converts text to natural, clear speech using `pyttsx3`.
- **Weather Information**: Retrieves real-time weather data through the OpenWeatherMap API.
- **Joke Fetching**: Provides entertainment with jokes from an integrated online API.
- **Timer and Alarm Management**: Enables setting, managing, and customizing timers and alarms.
- **Gemini Model Integration**: Utilizes the Gemini API Model for extensive knowledge with minimal GPU strain on lower-end devices.
- **Natural Language Processing (NLP)**: Leverages `nltk`, `sklearn`, and Gemini for advanced NLP and intent classification.
- **Bluetooth and NFC Scanning**: Detects and interacts with nearby Bluetooth and NFC devices (feature may vary).
- **Dictionary and Thesaurus**: Offers word definitions and synonyms through `PyDictionary`.
- **Currency Conversion**: Converts currencies with `forex-python` for financial management.
- **News Retrieval**: Keeps users updated with top news headlines via the NewsAPI.
- **Enhanced Conversations**: Facilitates engaging and meaningful conversations with the AI.
- **Computer Vision**: Provides object recognition and problem-solving capabilities (currently in development).
- **Interactive Games**: Includes rock-paper-scissors and coin flip for casual interaction.
- **Greetings**: Greets users with time and date information upon startup.
- **End-to-End Encryption**: Ensures all communications are encrypted, upholding user privacy and security.

---

## 🛠️ Installation and Prerequisites

### Prerequisites

- **Python 3.7+**: Ensure Python 3.7 or higher is installed.
- **Required Libraries**: Install dependencies listed in `requirements.txt`.

### Installation Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/N.I.R.A.git
    cd N.I.R.A
    ```

2. **Set Up a Virtual Environment (Recommended)**

    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configuration**

    - **API Keys**: Obtain and configure API keys for Google Custom Search, OpenWeatherMap, NewsAPI, and other services.
    - **Configuration File**: Create a `.env` file in the root directory to include your API keys and settings.

---

## 🔧 How It Works

### Voice Recognition

The `speech_recognition` library processes spoken commands, converting audio input into text and executing the corresponding actions.

### Text-to-Speech

`pyttsx3` is used to convert text into speech, providing natural and clear audio responses.

### Weather Information

Fetches current weather conditions and forecasts for specified locations using the OpenWeatherMap API.

### Joke Fetching

Delivers jokes from an online API to engage and entertain users.

### Timer and Alarm Management

Allows users to set, manage, and customize timers and alarms with adjustable alert sounds and durations.

### Gemini Model

Employs the Gemini API Model for comprehensive knowledge with minimal impact on GPU performance.

### Natural Language Processing (NLP)

Uses `nltk`, `sklearn`, and Gemini for sophisticated NLP and intent classification, enabling precise understanding and response.

### Bluetooth and NFC Scanning

Detects nearby Bluetooth and NFC devices for potential interactions (availability may vary).

### Dictionary Lookup

Provides word definitions, synonyms, and usage examples via `PyDictionary`.

### Currency Conversion

Converts currency amounts using the `forex-python` library to assist with financial tasks.

### News Retrieval

Fetches top news headlines from multiple sources with the NewsAPI to keep users informed.

### Conversations

Facilitates meaningful dialogues with the AI for a more engaging experience.

### Computer Vision

Offers object recognition and problem-solving capabilities (feature is under development).

### Rock Paper Scissors

Play a classic game of rock-paper-scissors with the AI.

### Coin Flip

Provides a fun coin-flipping feature for casual use.

### Greetings

Greets users with time and date information each time the application is started.

### End-to-End Encryption

Guarantees that all data transmissions are encrypted, safeguarding user privacy.

---

## 🚧 Roadmap

- **Expand Platform Support**: Enhance compatibility for additional operating systems, including macOS and Linux.
- **Enhance AI Capabilities**: Improve AI responses and contextual understanding.
- **Mobile App Development**: Develop a user-friendly mobile application.
- **Feature Expansion**: Integrate user-requested features and improvements.
- **User Experience Enhancements**: Refine UI/UX based on user feedback.

---

## 🤝 Contributing

We welcome contributions to enhance N.I.R.A. Here’s how you can get involved:

1. **Fork the Repository**: Create your own fork on GitHub.
2. **Create a Branch**: Develop your changes on a separate branch.
3. **Implement Changes**: Make modifications and ensure thorough testing.
4. **Submit a Pull Request**: Open a pull request with a detailed description of your changes.

For detailed guidelines, refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## 🦺 Support

For assistance or issues, please reach out on Discord: **[@nightblobby](https://discord.com/users/nightblobby)**

---

## 📬 Contact

For questions, feedback, or collaboration opportunities, contact me on Discord: **[@nightblobby](https://discord.com/users/nightblobby)**

---
