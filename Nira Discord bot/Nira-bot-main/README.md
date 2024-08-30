# NIRA - Neural Interactive Responsive Agent

![NIRA Logo](https://i.imgur.com/LOqyPNj.png)

## Overview

**NIRA** (Neural Interactive Responsive Agent) is an AI-powered Discord bot created using GPT-4 and developed by Shapes Inc. NIRA is designed to be your go-to companion for a wide range of tasks, from helping with homework to providing entertainment, and even being your best friend on Discord! NIRA is built to be intelligent, goofy, and engaging, ensuring a unique and fun experience for all users.

## Features

- **Powered by GPT-4o**: Leverages the latest AI technology to understand and respond naturally to user commands.
- **Homework Help**: Assists with homework and answers questions across various subjects.
- **Interactive and Fun**: Engages users with games, jokes, and fun commands.
- **Best Friend**: Provides friendly interactions and can even become your virtual best friend!
- **Moderation Tools**: Offers moderation commands to help manage your Discord server.
- **Image Manipulation**: Features commands for editing and manipulating images directly within Discord.
- **Customization**: Highly customizable responses and behavior tailored to user preferences.

## Getting Started

### Prerequisites

- **Python 3.8+**: Make sure Python is installed on your system.
- **Discord.py**: Install the Discord API wrapper for Python.
- **Other Libraries**: Install required dependencies like `requests`, `nltk`, `Pillow`, etc.

### Installation

Follow these steps to get NIRA up and running on your Discord server:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/nira-discord-bot.git
   cd nira-discord-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Discord bot token:
   - Create a new application in the [Discord Developer Portal](https://discord.com/developers/applications)
   - Add a bot to your application and copy the bot token
   - Create a `.env` file in the project root and add your token:
     ```
     DISCORD_TOKEN=your_bot_token_here
     ```

4. Run the bot:
   ```
   python main.py
   ```

## Usage

Once NIRA is running and added to your Discord server, you can start using its commands. Here are some examples:

- `.help`: Display the help menu with available commands
- `.homework <subject> <question>`: Get help with homework
- `.play <game>`: Start a game session
- `.image <command> <parameters>`: Manipulate images

For a full list of commands and their usage, refer to the in-bot help menu or the documentation.

## Help Command

NIRA provides a comprehensive help command to assist users in exploring its functionalities.

```
Welcome to the N.I.R.A Help Menu!

Use the dropdown below to select a command category. Each category provides detailed information about the commands available within it.

You can also use the .help <command> command to get specific information on any command.

Categories:
ℹ️ General - General bot commands.

🖼️ Image - Commands related to image manipulation.

🎮 Games - Fun games to play within Discord.

🛡️ Moderation - Moderation tools for server admins.

🎉 Fun - Miscellaneous and fun commands to enjoy.

How to Use the Help Command:
- Dropdown Navigation: Use the dropdown menu in the help interface to browse different command categories.
- Direct Command Help: Type .help <command> to get detailed information on how to use a specific command.
```

## Contributing

We welcome contributions to NIRA! If you'd like to contribute, please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

Please ensure your code adheres to our coding standards and include tests for new features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

For more information, visit our [website](https://www.nira-bot.com) or join our [Discord community](https://discord.gg/MB5QnVErhr).
