import pyttsx3
import time

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate",85)

# List of codes to be read out
codes = [
"APP60484",
"APP61011",
"APP60660",
"APP57647",
"APP59927",
"APP60854",
"APP58887",
"APP65727",
"APP58000",
"APP62443",
"APP57733",
"APP66962",
"APP59114",
"APP58554",
"APP60233",
"APP58225",
"APP60267",
"APP60144",
"APP57711",
"APP51610",
"APP60620",
"APP53972",
"APP52090",
"APP66726"]

# Function to read out each code with a delay
def read_codes(codes, delay):
    for code in codes:
        engine.say(code)
        engine.runAndWait()
        time.sleep(delay)

# Read the codes with a 2-second interval
read_codes(codes, 6)
