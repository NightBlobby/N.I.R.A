import discord
from utils.custom_colors import custom_colors
import random


def get_help_embed(page: int) -> discord.Embed:
    """Return the help embed for the specified page."""
    total_pages = 16  # Updated total pages count
    help_pages = [
        {
            "title":
            "Embed Creator Wizard Help - Overview",
            "description": ("```yaml\n"
                            "Pages:\n"
                            "1. Overview (this page)\n"
                            "2. Author\n"
                            "3. Body\n"
                            "4. Images\n"
                            "5. Footer\n"
                            "6. Schedule Embed\n"
                            "7. Send Button\n"
                            "8. Send To Button\n"
                            "9. Reset Embed Button\n"
                            "10. Edit Fields Button\n"
                            "11. Add Field Button\n"
                            "12. Remove Field Button\n"
                            "13. Help Button\n"
                            "14. Example Embed\n"
                            "15. Additional Tips\n"
                            "16. Navigation Buttons\n"
                            "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Author",
            "description":
            ("```yaml\n"
             "Author:\n\n"
             "- Author Name: The name of the author.\n\n"
             "- Author URL: A URL to link the author's name.\n\n"
             "- Author Icon URL: A URL to an image to display as the author's icon.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Body",
            "description":
            ("```yaml\n"
             "Body:\n\n"
             "- Title: The title of the embed.\n\n"
             "- Description: The main content of the embed.\n\n"
             "- URL: A URL to link the title.\n\n"
             "- Color: The color of the embed (hex code, color name, or 'random').\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Images",
            "description":
            ("```yaml\n"
             "Images:\n\n"
             "- Image URL: A URL to an image to display in the embed.\n\n"
             "- Thumbnail URL: A URL to a thumbnail image to display in the embed.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Footer",
            "description":
            ("```yaml\n"
             "Footer:\n\n"
             "- Footer Text: The text to display in the footer.\n\n"
             "- Footer Icon URL: A URL to an image to display as the footer icon.\n\n"
             "- Timestamp: The timestamp to display in the footer (YYYY-MM-DD hh:mm or 'auto').\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Send Button",
            "description":
            ("```yaml\n"
             "Send Button:\n\n"
             "- Description: This button allows you to send the configured embed to the current channel.\n\n"
             "- Functionality: It checks if the embed is properly configured and, if valid, sends it as a message.\n\n"
             "- Note: Ensure that you have at least one part of the embed configured before attempting to send it.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Send To Button",
            "description":
            ("```yaml\n"
             "Send To Button:\n\n"
             "- Description: This button allows you to send the configured embed to a specific channel.\n\n"
             "- Functionality: It opens a dropdown menu with a list of channels you have permission to send messages in.\n\n"
             "- Note: The embed must be properly configured before you can send it.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Reset Embed Button",
            "description":
            ("```yaml\n"
             "Reset Embed Button:\n\n"
             "- Description: This button resets the entire embed, clearing all the configurations you've made.\n\n"
             "- Functionality: It gives you a fresh start to create a new embed.\n\n"
             "- Note: Be cautious when using this, as all your settings will be lost.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Edit Fields Button",
            "description":
            ("```yaml\n"
             "Edit Fields Button:\n\n"
             "- Description: This button allows you to edit existing fields in the embed.\n\n"
             "- Functionality: It opens a dropdown menu with all current fields. Selecting a field opens a modal to edit its name, value, and inline status.\n\n"
             "- Note: You must have at least one field in the embed to use this button.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Add Field Button",
            "description":
            ("```yaml\n"
             "Add Field Button (➕):\n\n"
             "- Description: This button allows you to add a new field to the embed.\n\n"
             "- Functionality: It opens a modal where you can enter the name, value, and inline status of the new field.\n\n"
             "- Note: An embed can have up to 25 fields.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Remove Field Button",
            "description":
            ("```yaml\n"
             "Remove Field Button (➖):\n\n"
             "- Description: This button allows you to remove an existing field from the embed.\n\n"
             "- Functionality: It opens a dropdown menu with all current fields. Selecting a field removes it from the embed.\n\n"
             "- Note: You must have at least one field in the embed to use this button.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Help Button",
            "description":
            ("```yaml\n"
             "Help Button:\n\n"
             "- Description: This button opens this help menu.\n\n"
             "- Functionality: It provides detailed information about how to use the Embed Creator Wizard.\n\n"
             "- Note: You can navigate through different help pages using the navigation buttons at the bottom.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Example Embed",
            "description":
            ("```yaml\n"
             "Example Embed:\n\n"
             "- Title: Example Title\n"
             "- Description: This is an example embed.\n"
             "- URL: https://example.com\n"
             "- Color: #FF5733\n"
             "- Image URL: https://example.com/image.png\n"
             "- Thumbnail URL: https://example.com/thumbnail.png\n"
             "- Footer Text: Example Footer\n"
             "- Footer Icon URL: https://example.com/footer-icon.png\n"
             "- Timestamp: 2024-08-11 12:00\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Additional Tips",
            "description":
            ("```yaml\n"
             "Additional Tips:\n\n"
             "- Tip 1: Use the preview feature to see how your embed will look before sending it.\n"
             "- Tip 2: Make sure all URLs are valid and accessible.\n"
             "- Tip 3: Use consistent colors and formatting for a professional appearance.\n"
             "- Tip 4: Test the embed with different data to ensure it displays correctly in various scenarios.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Navigation Buttons",
            "description":
            ("```yaml\n"
             "Navigation Buttons:\n\n"
             "- Previous: Move to the previous help page.\n"
             "- Next: Move to the next help page.\n"
             "- Jump to Page: Open a modal to enter a specific page number to jump to.\n\n"
             "Note: These buttons appear at the bottom of each help page for easy navigation.\n"
             "```"),
        },
        {
            "title":
            "Embed Creator Wizard Help - Schedule Embed",
            "description":
            ("```yaml\n"
             "Schedule Embed:\n\n"
             "- Description: This feature allows you to schedule an embed to be sent at a later time.\n\n"
             "- Schedule Time: Enter when you want the embed to be sent. You can use:\n"
             "  - Relative time: e.g., 1m (1 minute), 1h (1 hour), 1d (1 day), 1w (1 week)\n"
             "  - Absolute time: YYYY-MM-DD HH:MM format\n\n"
             "- Channel ID: Enter the ID of the channel where you want the embed to be sent.\n\n"
             "- Note: Make sure the bot has permission to send messages in the specified channel.\n"
             "```"),
        },
    ]
    embed = discord.Embed(title=help_pages[page - 1]["title"],
                          description=help_pages[page - 1]["description"],
                          color=discord.Color.from_rgb(
                              *random.choice(list(custom_colors.values()))))
    embed.set_footer(text=f"Page {page}/{total_pages}")
    return embed
