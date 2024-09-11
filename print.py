import usb.core
import usb.util
from PIL import Image, ImageOps, ImageEnhance

# Function to open a USB printer
def find_usb_printer(vendor_id, product_id):
    # Find the USB device using vendor and product IDs
    dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    if dev is None:
        raise ValueError("Thermal Printer not found. Check connection.")
    
    # Detach kernel driver if necessary (for Linux)
    if dev.is_kernel_driver_active(0):
        dev.detach_kernel_driver(0)
    
    # Set active configuration
    dev.set_configuration()
    
    return dev

# Function to find the OUT endpoint
def find_out_endpoint(dev):
    # Iterate over all configurations, interfaces, and endpoints to find the OUT endpoint
    for cfg in dev:
        for interface in cfg:
            for ep in interface:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                    return ep.bEndpointAddress
    raise ValueError("Could not find an OUT endpoint on the printer.")

# Function to process the image (invert colors, adjust contrast, and resize for the printer)
def process_image(image_path, max_width=384, enhance_factor=1.5):
    # Open the image using Pillow
    img = Image.open(image_path)
    
    # Convert the image to grayscale
    img = img.convert('L')

    # Enhance the contrast of the image
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(enhance_factor)

    # Resize image while maintaining the aspect ratio
    width, height = img.size
    aspect_ratio = height / float(width)
    new_height = int(aspect_ratio * max_width)
    img = img.resize((max_width, new_height), Image.NEAREST)  # Faster resizing

    # Convert image to black and white
    img = img.convert('1')  # '1' mode converts image to 1-bit pixels, black and white

    # Invert the image (so that black is printed, white is not)
    img = ImageOps.invert(img)

    return img

# Function to send the image to the thermal printer using ESC/POS commands
def print_image(printer, out_endpoint, image):
    # Convert the image to a binary bytearray
    image_bytes = image.tobytes()

    # Calculate image dimensions
    width, height = image.size
    bytes_per_row = width // 8  # 8 pixels per byte

    # ESC/POS Command to set the printer in image mode
    ESC_POS_IMAGE_MODE = b'\x1d\x76\x30\x00'

    # Prepare header (width and height of the image in bytes)
    header = ESC_POS_IMAGE_MODE + bytes([bytes_per_row % 256, bytes_per_row // 256, height % 256, height // 256])

    # Send header and image data to the printer
    printer.write(out_endpoint, header + image_bytes, timeout=5000)  # Set a 5-second timeout

# Main code to find the printer and print the image
def printTime(image_path):
    # USB vendor and product IDs for printer
    VENDOR_ID = 0x0483  # Your Vendor ID
    PRODUCT_ID = 0x5840  # Your Product ID

    try:
        #Find the printer
        dev = find_usb_printer(VENDOR_ID, PRODUCT_ID)

        #Find correct OUT endpoint
        out_endpoint = find_out_endpoint(dev)
        
        # Process image (convert to black & white, invert colors, and resize)
        img = process_image(image_path, enhance_factor=1.8)  # Adjust enhance_factor to tune contrast

        # Print the processed image
        print_image(dev, out_endpoint, img)

        # Send a form feed or line feed to ensure the print is complete
        dev.write(out_endpoint, b'\n\n', timeout=5000)

        print("Image sent to the thermal printer successfully!")

    except Exception as e:
        print(f"Error: {e}")



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




file_path = "shuttercount.txt"
count = read_shutter_count(file_path)

image_path = "pilaroid_" + str(count) + ".jpg"
printTime(image_path) 
