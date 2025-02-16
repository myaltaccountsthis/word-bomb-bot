import cv2
import pytesseract
import pyautogui
import pydirectinput
# import pygetwindow
import numpy as np
import sys
import csv
import random
import keyboard
import time

# print(pygetwindow.getAllTitles())

DEBUG_TIME = False

time_obj = {}
def start_time(label: str):
    time_obj[label] = time.time()
def end_time(label: str, force = False):
    if DEBUG_TIME or force:
        print(f"--> {label:8s} {time.time() - time_obj[label]:.3f}s")

CHAT_WIDTH = 400
TOP_BAR_HEIGHT = 80
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

Y_SPACING = 10
CHARACTER_HEIGHT = 50

class TesseractResult:
    def __init__(self, level, page_num, block_num, par_num, line_num, word_num, left, top, width, height, conf, text):
        self.level = int(level)
        self.page_num = int(page_num)
        self.block_num = int(block_num)
        self.par_num = int(par_num)
        self.line_num = int(line_num)
        self.word_num = int(word_num)
        self.left = int(left)
        self.top = int(top)
        self.width = int(width)
        self.height = int(height)
        self.conf = float(conf)
        self.text = text
    
    def __str__(self):
        return f"\"{self.text}\" ({self.left} {self.top} {self.width} {self.height})"

start_time("read")
with open("dictionaries/dictionary-yawl.txt", "r") as input:
    s = input.read()
    DICTIONARY = set(s.split("\n"))

print(f"Loaded {len(DICTIONARY)} words")
end_time("read")

available_words = DICTIONARY

def get_good_words(s: str) -> list[str]:
    return list(filter(lambda word: s in word, available_words))

def get_screenshot():
    return np.array(pyautogui.screenshot(region=(0, TOP_BAR_HEIGHT, SCREEN_WIDTH - CHAT_WIDTH, SCREEN_HEIGHT - TOP_BAR_HEIGHT)))

# run 'python main.py true' to take a new screenshot
screenshot = len(sys.argv) >= 2

def get_word():
    start_time("func")
    start_time("image")

    if screenshot:
        img = cv2.cvtColor(get_screenshot(), cv2.COLOR_BGR2RGB)
        cv2.imwrite("out/raw.png", img)
    else:
        img = cv2.imread("out/raw.png")
        
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    cv2.imwrite("out/gray.png", gray)

    # Apply thresholding to preprocess the image
    thresholded = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    cv2.imwrite("out/thresholded.png", thresholded)

    end_time("image")

    start_time("ocr1")
    # Run OCR on the preprocessed image
    reader = csv.DictReader(pytesseract.image_to_data(thresholded).split("\n"), delimiter="\t")
    result = [ TesseractResult(**row) for row in reader ]

    left_bound = -1
    right_bound = -1
    top_bound = -1
    text_height = -1

    for info in result:
        text = info.text
        if text.isupper():
            cleaned = "".join(filter(str.isalpha, text))
            if cleaned in available_words:
                available_words.remove(cleaned)
        if text.startswith("Quick"):
            left_bound = info.left
            text_height = info.height
            top_bound = info.top + info.height + Y_SPACING
        if text == "containing:":
            right_bound = info.left + info.width
            
    end_time("ocr1")

    word = ""
    if (left_bound != -1 and right_bound != -1 and top_bound != -1 and text_height != -1):
        start_time("ocr2")
        # Extract the letters to match
        middle = cv2.threshold(gray, 26, 255, cv2.THRESH_BINARY)[1]
        middle = middle[top_bound:top_bound + CHARACTER_HEIGHT, left_bound:right_bound]
        middle = cv2.resize(middle, fx=2, fy=2, dsize=(0, 0))
        middle = cv2.dilate(middle, np.ones((3, 3), np.uint8), iterations=1) # Grow the white
        cv2.imwrite("out/middle.png", middle)

        # psm6 assumes a single uniform block of text
        match: str = pytesseract.image_to_string(middle, config="--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ|l").strip()
        match = match.replace("|", "I").replace("l", "I")
        if len(match) == 0:
            print("Empty match, skipping")
        else:
            good_words = get_good_words(match)
            print("Found", len(good_words), "words that match", match)
            if (len(good_words) >= 1):
                # print(good_words[-10:])
                word = random.choice(good_words)
                # word = max(good_words, key=len)
                print(word)
        end_time("ocr2")
    end_time("func", force=True)
    return word

if (len(sys.argv) > 1 and sys.argv[1] == "loop"):
    loop_active = False
    loop_delay = .3
    toggle_key = 'F7'

    def toggle_loop():
        global loop_active
        loop_active = not loop_active
        print("Starting loop..." if loop_active else "Stopping loop...")

    def main_loop():
        global available_words
        while True:
            if loop_active:
                word = get_word()
                if word in available_words:
                    available_words.remove(word)
                if (len(word) > 0):
                    pyautogui.write(word, .05)
                    pydirectinput.press("enter")
                time.sleep(.2)
            else:
                time.sleep(loop_delay)
    
    def reset_dict():
        global available_words
        available_words = DICTIONARY
        print("Dictionary reset")

    keyboard.add_hotkey(toggle_key, toggle_loop)
    keyboard.add_hotkey('F8', reset_dict)
    main_loop()

else:
    get_word()

