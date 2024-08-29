import openai
import speech_recognition as sr
import pyttsx3
import time
import tkinter as tk
import threading
import cv2
from tkinter import scrolledtext

#OpenAI API key
openai.api_key = 'hidden cuz cant share key on GIT' 

#recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

running = False

def listen_to_speech():
#Listen to speech and return the recognized text
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=3)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError:
            return "Error with the speech recognition service."

def generate_response(text):
#Generate a response from OpenAI's language model
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.RateLimitError as e:
        return f"Rate limit exceeded: {e}. Please try again later."
    except openai.error.OpenAIError as e:
        return f"An error occurred: {e}"

def speak_text(text):
#Convert text to speech
    engine.say(text)
    engine.runAndWait()

def process_speech():
#Process speech input, generate response, and speak the response within a 3-second window
    global running
    while running:
        start_time = time.time()
        user_input = listen_to_speech()
        app.log_message(f"User: {user_input}")
        if user_input:
            response = generate_response(user_input)
            app.log_message(f"Response: {response}")
            speak_text(response)
        elapsed_time = time.time() - start_time
        remaining_time = max(0, 3 - elapsed_time)
        time.sleep(remaining_time)

def show_webcam():
#Show webcam feed
    cap = cv2.VideoCapture(0)
    while running:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('Webcam Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def start_processing():
#Start the speech processing and webcam feed in separate threads
    global running
    running = True
    app.update_status("Processing...")
    threading.Thread(target=process_speech, daemon=True).start()
    threading.Thread(target=show_webcam, daemon=True).start()

def stop_processing():
#Stop the speech processing and webcam feed
    global running
    running = False
    app.update_status("Stopped")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech-to-Speech LLM Bot")
        self.geometry("600x500")

        
        self.start_button = tk.Button(self, text="Start", command=start_processing)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self, text="Stop", command=stop_processing)
        self.stop_button.pack(pady=10)

        self.status_label = tk.Label(self, text="Status: Not Started")
        self.status_label.pack(pady=10)

        self.log_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=20, width=70)
        self.log_area.pack(pady=10)

    def log_message(self, message):
    #Log messages to the scrolled text area
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.yview(tk.END)

    def update_status(self, status):
    #Update the status label
        self.status_label.config(text=f"Status: {status}")

#Create and run the main application
app = Application()
app.mainloop()
