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
- 🎉 [Thank You](#-thank-you)

---

## 🎨 UI/UX Design

- **For Phone (Nothing Themed)**
  ![Nothing Phone UI](https://github.com/user-attachments/assets/e83f4fd6-9f4b-4827-8856-01d44ff9cc0e)
  Made by [ALI](https://x.com/AliFakhruddin13)

---

## 📜 Terms and Conditions (Tried Not to Make It Boring)

Welcome to N.I.R.A., your soon-to-be favorite AI assistant! Before we dive into the fun, let’s go over some important (and delightfully sarcastic) Terms and Conditions.

1. **Acceptance of Terms**  
By using N.I.R.A., you’re agreeing to these Terms and Conditions. Congratulations! You’re now part of an exclusive club of people who like to read the fine print.

2. **Usage Restrictions**  
N.I.R.A. is here to assist, entertain, and occasionally baffle you with her quirks. However, please use her powers responsibly. No world domination plans or karaoke competitions, please. Any attempts to misuse her might result in an endless loop of dad jokes.

3. **Updates and Upgrades**  
We’ll be updating N.I.R.A. with new features and improvements. If she suddenly starts giving you unsolicited life advice or begins quoting Shakespeare, it’s just part of her charm. No need to panic.

4. **Liability Disclaimer**  
While we strive to make N.I.R.A. as fantastic as possible, we can’t promise she won’t occasionally be a bit eccentric. If she suggests eating pizza for breakfast or gives you directions to a non-existent place, it’s all in the name of fun.

5. **Termination**  
If you ever decide N.I.R.A. isn’t quite your cup of tea, you can end her services anytime. Just be prepared for a dramatic farewell message, possibly involving a heartfelt rendition of “My Heart Will Go On.”

6. **Changes to Terms**  
We might update these Terms from time to time. Don’t worry, we’ll keep it as entertaining as this message, so you won’t mind reading it.

---

## 🌟 Key Features

- 🔒 **Privacy-Centric Design**: Operates entirely locally, ensuring no external data sharing or retention.
- 🤖 **Advanced AI Capabilities**: Delivers intelligent, context-aware responses and actions.
- 🎙️ **Voice Recognition**: Utilizes sophisticated speech recognition to understand and process commands.
- ✉️🔊 **Flexible Input**: Accepts both voice and text commands.
- 🗣️ **Text-to-Speech**: Converts text to natural, clear speech using `pyttsx3`.
- 🌦️ **Weather Information**: Retrieves real-time weather data through the OpenWeatherMap API.
- 😂 **Joke Fetching**: Provides entertainment with jokes from an integrated online API.
- ⏰ **Timer and Alarm Management**: Enables setting, managing, and customizing timers and alarms.
- 💡 **Gemini Model Integration**: Utilizes the Gemini API Model for extensive knowledge with minimal GPU strain on lower-end devices.
- 🧠 **Natural Language Processing (NLP)**: Leverages `nltk`, `sklearn`, and Gemini for advanced NLP and intent classification.
- 📱🔍 **Bluetooth and NFC Scanning**: Detects and interacts with nearby Bluetooth and NFC devices (feature may vary).
- 📚 **Dictionary and Thesaurus**: Offers word definitions and synonyms through `PyDictionary`.
- 💱 **Currency Conversion**: Converts currencies with `forex-python` for financial management.
- 📰 **News Retrieval**: Keeps users updated with top news headlines via the NewsAPI.
- 💬 **Enhanced Conversations**: Facilitates engaging and meaningful conversations with the AI.
- 👁️ **Computer Vision**: Provides object recognition and problem-solving capabilities (currently in development).
- 🎲🪙 **Interactive Games**: Includes rock-paper-scissors and coin flip for casual interaction.
- 🌅 **Greetings**: Greets users with time and date information upon startup.
- 🔐 **End-to-End Encryption**: Ensures all communications are encrypted, upholding user privacy and security.

---

## 🛠️ Installation and Prerequisites

### Prerequisites

- **Python 3.7+**: Ensure you have Python 3.7 or higher installed.
- **Required Libraries**: Install the dependencies listed in `requirements.txt`.

### Installation Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/N.I.R.A.git
    cd N.I.R.A
    ```

2. **Set Up a Virtual Environment (Recommended)**

    Create and activate a virtual environment to manage dependencies:

    - **On macOS/Linux:**

      ```bash
      python -m venv venv
      source venv/bin/activate
      ```

    - **On Windows:**

      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

3. **Install Dependencies**

    Install the required libraries:

    ```bash
    pip install -r requirements.txt
    ```

4. **Configuration**

    - **API Keys**: Obtain API keys for any services you are using (e.g., OpenAI, weather APIs).
    - **Configuration File**: Create a `.env` file in the root directory of the project and include your API keys and settings.

    ```plaintext
    # Example .env file
    OPENAI_API_KEY=your_openai_api_key
    WEATHER_API_KEY=your_weather_api_key
    ```

5. **Run the Application**

    After setting up, you can start the application by running:

    ```bash
    python main.py
    ```

### 💡 Tips

- **Virtual Environment**: Using a virtual environment helps keep your project's dependencies isolated from other projects.
- **Configuration File**: Ensure that your `.env` file is secure and never commit it to version control. Use a `.gitignore` file to exclude it.

---

## 🔧 How It Works

- **Voice Recognition 🎙️**  
  The `speech_recognition` library processes spoken commands, converting audio input into text and executing the corresponding actions.

- **Text-to-Speech 🗣️**  
  `pyttsx3` is used to convert text into speech, providing natural and clear audio responses.

- **Weather Information 🌦️**  
  Fetches current weather conditions and forecasts for specified locations using the OpenWeatherMap API.

- **Joke Fetching 😂**  
  Delivers jokes from an online API to engage and entertain users.

- **Timer and Alarm Management ⏰**  
  Allows users to set, manage, and customize timers and alarms with adjustable alert sounds and durations.

- **Gemini Model 💡**  
  Employs the Gemini API Model for comprehensive knowledge with minimal impact on GPU performance.

- **Natural Language Processing (NLP) 🧠**  
  Uses `nltk`, `sklearn`, and Gemini for sophisticated NLP and intent classification, enabling precise understanding and response.

- **Bluetooth and NFC Scanning 📱🔍**  
  Detects nearby Bluetooth and NFC devices for potential interactions (availability may vary).

- **Dictionary Lookup 📚**  
  Provides word definitions, synonyms, and usage examples via `PyDictionary`.

- **Currency Conversion 💱**  
  Converts currency amounts using the `forex-python` library to assist with financial tasks.

- **News Retrieval 📰**  
  Fetches top news headlines from multiple sources with the NewsAPI to keep users informed.

- **Conversations 💬**  
  Facilitates meaningful dialogues with the AI for a more engaging experience.

- **Computer Vision 👁️**  
  Offers object recognition and problem-solving capabilities (feature is under development).

- **Rock Paper Scissors 🎲**  
  Play a classic game of rock-paper-scissors with the AI.

- **Coin Flip 🪙**  
  Provides a fun coin-flipping feature for casual use.

- **Greetings 🌅**  
  Greets users with time and date information each time the application is started.

- **End-to-End Encryption 🔐**  
  Guarantees that all data transmissions are encrypted, safeguarding user privacy.

---

## 🚧 Roadmap

- 🖥️ **Expand Platform Support**: Enhance compatibility for additional operating systems, including macOS and Linux.
- 🤖 **Enhance AI Capabilities**: Improve AI responses and contextual understanding.
- 📱 **Mobile App Development**: Develop a user-friendly mobile application.
- 🔧 **Feature Expansion**: Integrate user-requested features and improvements.
- 🎙️ **Voice Modulation**: Introduce voice modulation options for enhanced user interaction.
- 🌍 **Multilingual Support**: Extend support for multiple languages.
- 💬 **Advanced Chat Interface**: Develop a more sophisticated chat interface for natural conversations.
- 🔍 **Better Search Algorithms**: Improve search algorithms for more accurate results.
- 🚀 **Performance Optimization**: Continually optimize performance for faster response times.
- 🤝 **Third-Party Integrations**: Add more integrations with popular apps and services.

---

## 🤝 Contributing

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get involved.

### How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add feature'`).
5. Push to the branch (`git push origin feature-name`).
6. Open a Pull Request.

---

## 🦺 Support

If you encounter any issues or have questions, please check our [FAQ](FAQ.md) or open a [GitHub Issue](https://github.com/your-username/N.I.R.A/issues).

---

## 📬 Contact

For any inquiries, reach out to us via email at `support@nira.com` or follow us on [Twitter](https://twitter.com/nightblobby).

---

## 🎉 Thank You

Thank you for using N.I.R.A! We’re excited to have you on board and look forward to your feedback. Together, let’s make N.I.R.A the most advanced AI assistant in the universe! 🚀

--- 
