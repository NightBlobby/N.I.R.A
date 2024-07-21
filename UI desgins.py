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
from tkinter import scrolledtext
import datetime

def handle_button_click(button_text):
    if button_text == "Listen...":
        # Implement the listening functionality
        pass
    elif button_text == "Theme":
        # Implement the theme change functionality
        pass
    elif button_text == "Help!":
        # Implement the help functionality
        pass

def get_time_date_day():
    now = datetime.datetime.now()
    return now.strftime("%I:%M:%S %p"), now.strftime("%B %d, %Y"), now.strftime("%A")

def update_time_date_day():
    current_time, current_date, current_day = get_time_date_day()
    time_label.config(text=current_time)
    date_label.config(text=current_date)
    day_label.config(text=current_day)
    root.after(1000, update_time_date_day)

def create_ui():
    global root, header_frame, header_label, main_frame, sidebar_frame, logo_label, content_frame, welcome_label, footer_label, command_history_text, time_label, date_label, day_label

    root = tk.Tk()
    root.title("AI Assistant")
    root.geometry("800x600")
    root.configure(bg="#1E1E1E")  # Set background color

    # Header
    header_frame = tk.Frame(root, bg="#222222", padx=10, pady=10)
    header_frame.pack(side=tk.TOP, fill=tk.X)

    header_label = tk.Label(header_frame, text="AI Assistant", font=("Arial", 24, "bold"), bg="#222222", fg="#FFFFFF")
    header_label.pack()

    # Main content area
    main_frame = tk.Frame(root, bg="#1E1E1E")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Left sidebar
    sidebar_frame = tk.Frame(main_frame, bg="#222222", width=200)
    sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

    nav_buttons = ["Listen...", "Theme", "Help!"]
    for button_text in nav_buttons:
        button = tk.Button(sidebar_frame, text=button_text, font=("Arial", 14), bg="#10ac84", fg="#FFFFFF", width=15, bd=0, highlightthickness=0, command=lambda b=button_text: handle_button_click(b))
        button.pack(pady=5)

    # Main content area (right side)
    content_frame = tk.Frame(main_frame, bg="#1E1E1E")
    content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Welcome label (replaced with time/date/day labels)
    time_date_day_frame = tk.Frame(content_frame, bg="#1E1E1E", padx=10, pady=10)
    time_date_day_frame.pack(pady=10)

    time_label = tk.Label(time_date_day_frame, text="", font=("Arial", 24), bg="#1E1E1E", fg="#FFFFFF")
    time_label.grid(row=0, column=0, padx=10)

    date_label = tk.Label(time_date_day_frame, text="", font=("Arial", 16), bg="#1E1E1E", fg="#FFFFFF")
    date_label.grid(row=1, column=0, padx=10)

    day_label = tk.Label(time_date_day_frame, text="", font=("Arial", 16), bg="#1E1E1E", fg="#FFFFFF")
    day_label.grid(row=2, column=0, padx=10)

    update_time_date_day()

    # Command history text box
    command_history_label = tk.Label(content_frame, text="Command History", font=("Arial", 16), bg="#1E1E1E", fg="#FFFFFF")
    command_history_label.pack(pady=(0, 10))

    command_history_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=40, height=10, font=("Arial", 12), bg="#222222", fg="#FFFFFF")
    command_history_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Footer
    footer_label = tk.Label(root, text="© 2024 NightBlobby. All rights reserved.", font=("Arial", 10), bg="#222222", fg="#FFFFFF", anchor="se", padx=10, pady=5)
    footer_label.pack(fill=tk.X, side=tk.BOTTOM)

    root.mainloop()

create_ui()
