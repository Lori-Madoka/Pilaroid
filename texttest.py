from PIL import Image, ImageFont, ImageDraw
from luma.core.render import canvas
import time
import random
import RPi.GPIO as GPIO
import subprocess
import os
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
import usb.core
import usb.util

# Raspberry Pi pin configuration
BUTTON_PIN = 17  # GPIO pin 17 (physical pin 11)
SHUTDOWN_HOLD_TIME = 10  # Time in seconds to hold the button for shutdown
DEBOUNCE_TIME = 0.3  # Debounce time in seconds

# Initialize I2C interface and the OLED display
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, height=32, width=128)  # Ensure correct dimensions

# Load a smaller or default font
font = ImageFont.load_default()  # Fallback to default font

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Function to open a USB printer
def find_usb_printer(vendor_id, product_id):
    # Find the USB device using vendor and product IDs
    dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    if dev is None:
        raise ValueError("Thermal Printer not found. Check connection.")
        display_text("Error: printer unfound")
    
    # Detach kernel driver if necessary (for Linux)
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    
    # Set active configuration
    dev.set_configuration()
    
    return dev

def read_shutter_count(file_path):
    try:
        with open(file_path, 'r') as file:
            count = int(file.read().strip())
    except FileNotFoundError:
        count = 0  # Start at 0 if file doesn't exist
    return count

def write_shutter_count(file_path, count):
    with open(file_path, 'w') as file:
        file.write(str(count))

# Function to display text on the OLED
def display_text(text):
    image = Image.new('1', (device.width, device.height))
    draw = ImageDraw.Draw(image)
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = ((device.width - text_width) // 2)
    y = ((device.height - text_height) // 2) - 4 
    
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.text((x, y), text, font=font, fill=255)
    rotated_image = image.rotate(180)
    device.display(rotated_image)

# Initial message
display_text("booting...")

def startuptextboiiiiii():
    print("It did thee silly")
    line_number = random.randint(1, 20)
    with open('startup.txt', 'r') as file:
        lines = file.readlines()
    for i in range(8):
        specific_line = lines[line_number - 1]
        display_text(specific_line)
        line_number = random.randint(1, 20)
        time.sleep(0.4)

time.sleep(2)
startuptextboiiiiii()

shutter_count_file = 'shuttercount.txt'
shutter_count = read_shutter_count(shutter_count_file)

def shutdown_pi():
    display_text("Shutting down...")
    os.system("sudo shutdown now")

def take_picture():
    global shutter_count
    display_text("Capturing a memory!")
    
    shutter_count = read_shutter_count(shutter_count_file)
    shutter_count += 1
    write_shutter_count(shutter_count_file, shutter_count)
    
    output_filename = f'pilaroid_{shutter_count:04d}.jpg'
    command = [
        'libcamera-still',
        '-o', output_filename,
        '--autofocus-on-capture',
        '--width', '1080',
        '--height', '1080',
        '--nopreview',
        '--immediate'
    ]
    
    try:
        subprocess.run(command, check=True)
        display_text(f"Photo saved as {output_filename}")
    except subprocess.CalledProcessError as e:
        display_text(f"Error: {e}")
    
    time.sleep(0.5)  # Debounce delay
    display_text("Capture complete")
    time.sleep(0.2)
    display_text("Printing image...")
    
    result = subprocess.run(["python3", "printertest.py"], capture_output=True, text=True)
    # Print the output and error (if any)
    print("Output:", result.stdout)
    print("Error:", result.stderr)

    display_text(result.stdout)
    
    display_text("Print complete :)")
    time.sleep(0.2)

def monitor_button_press():
    press_start_time = None

    while True:
        button_state = GPIO.input(BUTTON_PIN)
        
        if button_state == GPIO.LOW:  # Button is pressed
            if press_start_time is None:
                press_start_time = time.time()
            else:
                elapsed_time = time.time() - press_start_time
                
                if elapsed_time >= SHUTDOWN_HOLD_TIME:
                    display_text("disabling power usage")
                    time.sleep(1)
                    display_text(" ")
                    shutdown_pi()
                    break

        else:  # Button is released
            if press_start_time is not None:
                elapsed_time = time.time() - press_start_time
                
                if elapsed_time < SHUTDOWN_HOLD_TIME:
                    take_picture()
                
                press_start_time = None  # Reset press start time

        time.sleep(0.1)  # Small delay to reduce CPU usage

def run_animation():
    try:
        fpstime = 0.001
        while True:
            display_text("|W<                         ") 
            time.sleep(fpstime)
            display_text("|WO                         ") 
            time.sleep(fpstime)
            display_text(" OWO                        ")
            time.sleep(fpstime)
            display_text("   OWO                      ")
            time.sleep(fpstime)
            display_text("       OWO                  ")
            time.sleep(fpstime)
            display_text("           OWO              ")
            time.sleep(fpstime)
            display_text("                OWO         ")
            time.sleep(fpstime)
            display_text("                     OWO    ")
            time.sleep(fpstime)
            display_text("                         OW|") 
            time.sleep(fpstime)
            display_text("                         >W|") 
            time.sleep(fpstime)
            display_text("                         >W|") 
            time.sleep(fpstime)
            display_text("                         OW|") 
            time.sleep(fpstime)
            display_text("                        OWO ")
            time.sleep(fpstime)
            display_text("                      OWO   ")
            time.sleep(fpstime)
            display_text("                  OWO       ")
            time.sleep(fpstime)
            display_text("             OWO            ")
            time.sleep(fpstime)
            display_text("        OWO                 ")
            time.sleep(fpstime)
            display_text("   OWO                      ")
            time.sleep(fpstime)
            display_text("|WO                         ")
            time.sleep(fpstime)
            display_text("|W<                         ") 
            time.sleep(fpstime)
    except KeyboardInterrupt:
        GPIO.cleanup()
    finally:
        GPIO.cleanup()

                        
# Start monitoring the button press and running the animation concurrently
button_thread = threading.Thread(target=monitor_button_press)
animation_thread = threading.Thread(target=run_animation)

button_thread.start()
animation_thread.start()

try:
    button_thread.join()
    animation_thread.join()
except KeyboardInterrupt:
    display_text(" ")
    GPIO.cleanup()
finally:
    display_text(" ")
    GPIO.cleanup()
