# HalowLink-Tracker
A tool used to map out coverage of a WiFi Halow network

This code will connect to a HalowLink2 (HalowLink1 and other Morse Micro based OpenWRT devices will probably work, untested) to pull signal stats and store it in a CSV file with GPS coordinates from a GPS receiver. The CSV can be imported into Google Earth or whatever you like to visualize the results.

This is the bare minimum code that I needed to collect the data, it sucks, it's fragile, use at your own risk.

The baudrate and USB serial port for the GPS are hardcoded. The router's credentials and IP are hardcoded. It will just crash if the router isn't reachable. 

Output is stored in the log-halow.csv file, I included an empty CSV with headers

Uses the following python packages:
pyserial - Used to connect to the USB/Serial GPS
pynmea2 - Decoding the GPS output
fabric - SSH to connect to the router