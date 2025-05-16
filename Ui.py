import tkinter as tk
import pyttsx3
from PIL import Image, ImageTk  # Use PIL for image resizing

def on_key_press(event):
    global current_word, full_text
    char = event.char
    if char.isalpha():
        current_word += char
    elif char == ' ':
        speak_text(current_word)
        current_word = ''
    text_display.config(text=current_word)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def stop_app():
    root.destroy()

# Initialize the main window
root = tk.Tk()
root.title("Keyboard Input Display")
root.geometry("300x400")

# Initialize text-to-speech engine
engine = pyttsx3.init()

current_word = ""
full_text = ""

# Load and resize Bluetooth icon
bluetooth_img = Image.open("bluetooth.png")
bluetooth_img = bluetooth_img.resize((60, 60), Image.Resampling.LANCZOS)
bluetooth_icon = ImageTk.PhotoImage(bluetooth_img)

# Display Bluetooth icon in the top-right corner
bluetooth_label = tk.Label(root, image=bluetooth_icon)
bluetooth_label.place(x=220, y=5)  # Adjust position for a small top-corner placement

text_display = tk.Label(root, text="", font=("Arial", 24), fg="black")
text_display.pack(pady=70)

current_word_label = tk.Label(root, text="Current Word", font=("Arial", 14), fg="grey")
current_word_label.place(x=90,y=110)

stop_button = tk.Button(root, text="STOP", font=("Arial", 20), bg="red", fg="white", command=stop_app)
stop_button.pack(pady=50)

root.bind("<Key>", on_key_press)
root.mainloop()
