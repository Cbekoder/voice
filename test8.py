import speech_recognition as sr

def recognize_speech():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Say something...")
            audio_data = recognizer.listen(source, timeout=5)

            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)
            print("You said:", text)

    except sr.WaitTimeoutError:
        print("No speech detected within the timeout.")
    except sr.UnknownValueError:
        print("Speech Recognition could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")

if __name__ == "__main__":
    recognize_speech()
