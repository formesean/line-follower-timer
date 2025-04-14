# Line Follower Timer Web Interface

A web-based interface for controlling and monitoring your line follower timer system. This system combines an Arduino-based hardware setup with a web interface to measure and display completion times for line-following robots or similar track-based projects.

## Hardware Requirements

- Arduino Uno
- VL53L0X Time-of-Flight Distance Sensor
- LCD Display (I2C interface, 16x2)
- Servo Motor
- Push Button
- HC-05 Bluetooth Module
- Appropriate power supply

## Initial Bluetooth Setup

1. **Pair HC-05 Module:**

   - Go to Windows Settings → "Bluetooth & other devices"
   - Click "Add Bluetooth or other device"
   - Select "Bluetooth"
   - Look for "HC-05" in the device list
   - When prompted, enter the default password: `1234`
   - **Note:** It's normal for the HC-05 to show as "Paired" but not "Connected" in Bluetooth settings

2. **Find the Correct COM Port:**
   - Go to Windows Settings → "Bluetooth & other devices"
   - Click "More Bluetooth settings"
   - Select the "COM Ports" tab
   - Look for "HC-05 'SSP Dev'" in the list
   - Note the COM port number that has "Outgoing" direction
   - This is the port number you'll need for the next step

## Software Installation

1. Clone or download this repository

2. Navigate to the `www` folder:

   ```bash
   cd www
   ```

3. Install dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the COM port:
   - Open `app.py` from the `www` folder
   - Locate the COM port configuration:
     ```python
     COM_PORT = "COM17"  # Change this to your Outgoing HC-05 COM port
     ```
   - Update it to match the Outgoing COM port number you found in the Bluetooth settings

## Running the Web Server

1. Make sure you're in the `www` folder

2. Start the Flask server:

   ```bash
     python app.py
   ```

3. Access the web interface at: `http://localhost:5000`

## Using the Web Interface

### Main Features

- Real-time timer display (MM:SS:mmm format)
- Status indicator showing current system state
- "Ready" button to start new timing sessions

### How to Use

1. Open `http://localhost:5000` in your web browser
2. Click the "Ready" button to prepare the system
3. The timer will:
   - Start automatically when the line follower crosses the start line
   - Update in real-time during the run
   - Display the final time when the finish line is crossed

### Display Information

- **Status Messages:**
  - "Waiting for signal..." - Initial state
  - "Timer running..." - During active run
  - "Final recorded time:" - After run completion
- **Timer Format:** MM:SS:mmm (minutes:seconds:milliseconds)

## Hardware Setup

### Arduino Connections

- VL53L0X sensor: Connect to I2C pins (SDA/SCL)
- LCD Display: Connect to I2C pins (SDA/SCL)
- Servo: Connect to pin 4
- Push Button: Connect to pin 8
- HC-05 Bluetooth Module:
  - RX: Connect to pin 3
  - TX: Connect to pin 2

### Sensor Placement

- Position the VL53L0X sensor at the finish line of your track
- Ensure the sensor has a clear line of sight to detect passing objects

## Troubleshooting

### Bluetooth Connection Issues

- Verify HC-05 is properly paired in Windows Bluetooth settings
- Double-check you're using the correct Outgoing COM port
- Try removing and re-pairing the HC-05 device
- Restart the Arduino if the connection seems unstable

### COM Port Issues

- Verify no other applications are using the COM port
- Check if the COM port number in `app.py` matches the Outgoing port in Bluetooth settings
- Try unplugging and reconnecting the Arduino

### Web Interface Issues

- Verify the Flask server is running
- Check if port 5000 is available
- Try refreshing the browser

### Hardware Issues

- Check all wire connections
- Verify the Arduino is properly powered
- Ensure the HC-05 module is receiving power
- Check if the VL53L0X sensor is properly connected and responding
- Verify the LCD display is properly connected to I2C

## System Features

- Automatic start/stop detection using ToF sensor
- Real-time timing display on both LCD and web interface
- Bluetooth communication between Arduino and computer
- Manual override using physical button
- Millisecond precision timing
- Celebratory servo movement upon completion
- Clean, responsive web interface design

## Notes

- The system uses a threshold of 300mm for object detection
- The web interface updates every 500ms
- The LCD displays time in MM:SS:mmm format
- The servo performs 4 sweeps as a completion celebration
