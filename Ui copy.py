import tkinter as tk
import pyttsx3
from PIL import Image, ImageTk  # Use PIL for image resizing

SCALE_FACTOR = 2

def on_key_press(event):
    global current_word, full_text
    char = event.char
    if char.isalpha():
        current_word += char.capitalize()
    elif char == ' ':
        speak_text(current_word)
        current_word = ''
    text_display.config(text=current_word)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def show_main_screen():
    start_frame.place_forget()
    main_frame.place(x=0, y=0, width=SCALE_FACTOR*300, height=SCALE_FACTOR*400)

def show_start_screen():
    global current_word
    current_word = ''
    text_display.config(text=current_word)
    main_frame.place_forget()
    start_frame.place(x=0, y=0, width=SCALE_FACTOR*300, height=SCALE_FACTOR*400)

def stop_app():
    show_start_screen()

def toggle_x_image():
    if x_label.winfo_ismapped():
        x_label.place_forget()
    else:
        x_label.place(x=SCALE_FACTOR*220, y=SCALE_FACTOR*5)  # Initially hidden

# Initialize the main window
root = tk.Tk()
root.title("Keyboard Input Display")
width = 300 * SCALE_FACTOR
hieght = 400 * SCALE_FACTOR
root.geometry(str(width) + "x" + str(hieght))

# Initialize text-to-speech engine
engine = pyttsx3.init()

current_word = ""
full_text = ""

# Load and resize Bluetooth icon
bluetooth_img = Image.open("bluetooth.png")
bluetooth_img = bluetooth_img.resize((SCALE_FACTOR*60, SCALE_FACTOR*60), Image.Resampling.LANCZOS)
bluetooth_icon = ImageTk.PhotoImage(bluetooth_img)

# Load and resize X_image
x_img = Image.open("bluetooth_not_connected.png")
x_img = x_img.resize((SCALE_FACTOR*60, SCALE_FACTOR*60), Image.Resampling.LANCZOS)
x_photo = ImageTk.PhotoImage(x_img)

# Load and resize hand image
hand_img = Image.open("hand.png")
hand_img = hand_img.resize((SCALE_FACTOR*100, SCALE_FACTOR*100), Image.Resampling.LANCZOS)
hand_icon = ImageTk.PhotoImage(hand_img)

# Create start screen frame
start_frame = tk.Frame(root, width=SCALE_FACTOR*300, height=SCALE_FACTOR*400)
start_frame.place(x=0, y=0, width=SCALE_FACTOR*300, height=SCALE_FACTOR*400)

start_label = tk.Label(start_frame, image=bluetooth_icon)
start_label.place(x=SCALE_FACTOR*220, y=SCALE_FACTOR*5)

x_label = tk.Label(start_frame, image=x_photo)
x_label.place(x=SCALE_FACTOR*220, y=SCALE_FACTOR*5)  # Initially hidden
# x_label.place_forget()

hand_sign = tk.Label(start_frame, image=hand_icon)
hand_sign.pack(pady = (100,0))

start_button = tk.Button(start_frame, text="START", font=("Arial", SCALE_FACTOR*20), bg="green", fg="white", command=show_main_screen)
start_button.place(x=SCALE_FACTOR*90, y=SCALE_FACTOR*300)

# Create main screen frame
main_frame = tk.Frame(root, width=SCALE_FACTOR*300, height=SCALE_FACTOR*400)

# Display Bluetooth icon in the top-right corner
bluetooth_label = tk.Label(main_frame, image=bluetooth_icon)
bluetooth_label.place(x=SCALE_FACTOR*220, y=SCALE_FACTOR*5)  # Adjust position for a small top-corner placement

text_display = tk.Label(main_frame, text="", font=("Arial", SCALE_FACTOR*24), fg="black")
text_display.pack(pady=(SCALE_FACTOR*90,0))

current_word_label = tk.Label(main_frame, text="Current Word", font=("Arial", SCALE_FACTOR*16), fg="grey")
current_word_label.pack(pady=SCALE_FACTOR*5)

mode_display = tk.Label(main_frame, text="MODE: FINGER SPELLING", font=("Arial", SCALE_FACTOR*16), fg="black")
mode_display.pack(pady=SCALE_FACTOR*5)

stop_button = tk.Button(main_frame, text="STOP", font=("Arial", SCALE_FACTOR*20), bg="red", fg="white", command=stop_app)
stop_button.place(x=SCALE_FACTOR*95, y=SCALE_FACTOR*300)

root.bind("<Key>", on_key_press)
root.mainloop()
