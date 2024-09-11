# Pilaroid
A raspberry pi in a Polaroid - the Pilaroid

## Dependencies
requires Luma (pip3 install luma)
requires PIL (pip3 install Pillow)
requires RPi.GPIO (pip3 install RPi.GPIO)

## Functionality
The Pilaroid prints an image upon capture (albeit with a slight delay).
Setup your pi to boot and auto log in and then set a script to autorun and start a virtual environment as well as run the python script, you will need a startup.txt for the boot up animation on the screen or just remove it from the code.
Single press of shutter button to take a photo, hold shutter button for 10 seconds to power off.
I am yet to find a reliable way of powering on the Pi from an off state without cycling the power supply.
