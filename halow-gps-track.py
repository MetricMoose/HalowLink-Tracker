import json, io, pynmea2, serial, threading, time, csv
from fabric import Connection
from datetime import datetime


# GPS runs in another thread 
lock = threading.Lock()
def gps_loop():

    # Storing the lat/long in decimal degrees
    global latitude
    global longitude
    
    latitude = 0
    longitude = 0

    # Setup USB serial connection for the GPS
    ser = serial.Serial('/dev/ttyUSB0', 4800, timeout=5.0)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), encoding='utf-8', errors='replace')

    # Repeatedly try to decode the NMEA data from the GPS and store the latitude/longitude in a variable 
    while 1:
        try:
            line = sio.readline()
            msg = pynmea2.parse(line)
            try:
                with lock:
                    latitude = msg.latitude
                    longitude = msg.longitude
            except:
                continue
        except serial.SerialException as e:
            print('Device error: {}'.format(e))
            continue
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue
            
thread = threading.Thread(target=gps_loop, daemon=True)
thread.start()

# Run every 5 seconds
while True:
    time.sleep(5)
    
    # Get JSON formatted wifi client info from OpenWRT over SSH
    # ToDo: Program just exits if the login fails
    assocList = Connection('root@192.168.12.99', connect_kwargs={"password": "routerpassword"}).run('ubus call iwinfo assoclist \'{\"device\":\"wlan0\"}\'', hide=True)

    # Decode the JSON output from ubus and store it as a list
    assocListJson = json.loads(assocList.stdout.strip())
    
    # A populated results section means that the wifi client is associated with the AP
    if assocListJson['results']:
        connected = True
        signal = assocListJson['results'][0]['signal']
        noise = assocListJson['results'][0]['noise']
        rxMhz = assocListJson['results'][0]['rx']['mhz']
        rxRate = assocListJson['results'][0]['rx']['rate']
        rxMcs = assocListJson['results'][0]['rx']['mcs']
        txMhz = assocListJson['results'][0]['tx']['mhz']
        txRate = assocListJson['results'][0]['tx']['rate']
        txMcs = assocListJson['results'][0]['tx']['mcs']
        
        # Debugging, spit out the signal data to the console
        print(f"Signal: {signal}, Noise: {noise}, rxMHz: {rxMhz}, rxRate: {rxRate}, rxMCS: {rxMcs}, txMHz: {txMhz}, txRate: {txRate}, txMCS: {txMcs}")
    else:
        connected = False
        print('Not Connected')

    # Debugging, spit out the lat/long to the console
    print(f"Lat: {latitude} Long: {longitude}")
    
    # Write CSV Log File to log-halow.csv, appending to the existing CSV that has the header row
    timestamp = datetime.now().isoformat()
    print(f"timestamp: {timestamp}")
    with open('log-halow.csv', 'a', newline='') as f:
        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        if connected:
            with lock:
                writer.writerow([timestamp, 'Connected', latitude, longitude, signal, noise, rxMhz, rxRate, rxMcs, txMhz, txRate, txMcs])
        else:
            with lock:
                writer.writerow([timestamp, 'Disconnected', latitude, longitude])
                
            
    
