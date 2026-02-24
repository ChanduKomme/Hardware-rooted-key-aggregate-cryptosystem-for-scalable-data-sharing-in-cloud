import os, json
import RPi.GPIO as GPIO
from time import sleep
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from mfrc522 import SimpleMFRC522
from sensors import lines_for_oled

# ---------------- GPIO / LED setup ----------------
LED_GREEN, LED_RED = 17, 27
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_GREEN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED_RED,   GPIO.OUT, initial=GPIO.LOW)

# ---------------- OLED setup ----------------
serial = i2c(port=1, address=0x3C)   # common SSD1306 I2C address
oled = ssd1306(serial, width=128, height=64)

# Monospace font fits best on 128x64
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
except Exception:
    font = ImageFont.load_default()

def show(lines):
    """Display up to 4 lines on the OLED."""
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    for i, line in enumerate((lines if isinstance(lines, list) else [str(lines)])[:4]):
        draw.text((0, i * 16), str(line), font=font, fill=255)
    oled.display(image)

def feedback(granted: bool, lines):
    """LED + OLED feedback for 2 seconds."""
    GPIO.output(LED_GREEN, GPIO.HIGH if granted else GPIO.LOW)
    GPIO.output(LED_RED,   GPIO.LOW  if granted else GPIO.HIGH)
    show(lines)
    sleep(2)
    GPIO.output(LED_GREEN, GPIO.LOW)
    GPIO.output(LED_RED,   GPIO.LOW)

# ---------------- Authorized tags (JSON allow-list) ----------------
AUTH_FILE = os.path.join(os.path.dirname(__file__), "authorized_tags.json")

def _load_authorized():
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return {int(k): v for k, v in d.items()}
    except Exception:
        return {}

AUTHORIZED_TAGS = _load_authorized()

def reload_authorized():
    global AUTHORIZED_TAGS
    AUTHORIZED_TAGS = _load_authorized()
    return AUTHORIZED_TAGS

# ---------------- RFID reader ----------------
_reader = SimpleMFRC522()

def rfid_check():
    """Block until a card is tapped. Returns (True, name) or (False, 'Unknown')."""
    # hot-reload new enrollments
    reload_authorized()

    env_lines = lines_for_oled()
    base = ["Security Verification", "Tap the card...", "Waiting..."]
    show((env_lines + base)[:4])

    uid, _ = _reader.read()   # blocking read
    uid = int(uid)

    name = AUTHORIZED_TAGS.get(uid)
    if name:
        feedback(True, [f"Hello {name}", "Access granted"]) 
        return True, name
    else:
        feedback(False, ["RFID denied", f"UID: {uid}"])
        return False, "Unknown"

# ---------------- Cleanup on exit ----------------
import atexit
@atexit.register
def _cleanup_gpio():
    try:
        GPIO.cleanup()
    except Exception:
        pass
