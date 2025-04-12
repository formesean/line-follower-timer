import threading
import time
import serial
from flask import Flask, jsonify, render_template_string, request

# --- Configuration ---
COM_PORT = "COM17"  # Change to your port (e.g., '/dev/ttyUSB0' for Linux)
BAUD_RATE = 9600
SERIAL_TIMEOUT = 1

# --- Global Data ---
start_timestamp = None
stop_timestamp = None
formatted_time = ""
latest_data = ""
data_lock = threading.Lock()

# --- Serial Port Setup ---
def connect_to_com_port(port_name, baud_rate=9600, timeout=1):
    try:
        ser = serial.Serial(port_name, baudrate=baud_rate, timeout=timeout)
        print(f"Successfully connected to {port_name}")
        return ser
    except serial.SerialException as e:
        print(f"Failed to connect to {port_name}: {e}")
        return None

# --- Background Thread to Read Serial Data ---
def serial_read_thread(serial_connection):
    global latest_data, start_timestamp, stop_timestamp, formatted_time
    while True:
        try:
            if serial_connection.in_waiting > 0:
                line = serial_connection.readline().decode('utf-8').strip()
                if line:
                    with data_lock:
                        latest_data = line
                        if line.startswith("START"):
                            start_timestamp = int(time.time() * 1000)
                            stop_timestamp = None
                            formatted_time = ""
                        elif line.startswith("STOP"):
                            stop_timestamp = int(time.time() * 1000)
                        elif line.startswith("TIME"):
                            formatted_time = line[5:].strip()
                    print(f"Received: {line}")
        except Exception as e:
            print(f"Error while reading data: {e}")
        time.sleep(0.01)

# --- Flask Web App Setup ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>Arduino Timer</title>
  <style>
    body {
      font-family: sans-serif;
      text-align: center;
      margin-top: 100px;
      background-color: #f4f7fc;
    }

    h1 {
      font-size: 2rem;
      color: #333;
    }

    #timer {
      font-size: 3rem;
      margin-top: 20px;
      color: #444;
    }

    #status {
      font-size: 1.25rem;
      color: #555;
      margin-top: 10px;
    }

    /* Button Styles */
    #simulatedButton {
      font-size: 1.2rem;
      padding: 12px 25px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.3s, transform 0.2s;
    }

    #simulatedButton:hover {
      background-color: #45a049;
      transform: scale(1.05);
    }

    #simulatedButton:active {
      background-color: #388e3c;
      transform: scale(0.98);
    }
  </style>
</head>
<body>
  <h1>Line Follower Timer</h1>
  <div id="status">Waiting for signal...</div>
  <div id="timer">00:00:000</div>
  <button id="simulatedButton">Ready</button>

  <script>
    let start = 0;
    let stop = null;
    let interval = null;

    document.getElementById('simulatedButton').addEventListener('click', async () => {
      try {
          await fetch('/simulate_button_press', {
            method: 'POST'
          });
      } catch (err) {
          console.error('Error pressing simulated button:', err);
      }
    });

    function formatTime(ms) {
      let minutes = Math.floor(ms / 60000);
      let seconds = Math.floor((ms % 60000) / 1000);
      let millis = ms % 1000;

      return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}:${String(millis).padStart(3, '0')}`;
    }

    async function fetchTimerData() {
      try {
        const res = await fetch('/timer');
        const { start: s, stop: e, formatted } = await res.json();

        if (s && !e) {
          if (!start || start !== s) {
            start = s;
            stop = null;
            document.getElementById('status').innerText = "Timer running...";
            if (interval) clearInterval(interval);
            interval = setInterval(() => {
              const now = Date.now();
              const elapsed = now - start;
              document.getElementById('timer').innerText = formatTime(elapsed);
            }, 50);
          }
        } else if (s && e && formatted) {
          if (!stop || stop !== e) {
            stop = e;
            clearInterval(interval);
            document.getElementById('status').innerText = "Final recorded time:";
            document.getElementById('timer').innerText = formatted;
          }
        }
      } catch (err) {
        console.error(err);
      }
    }

    setInterval(fetchTimerData, 500);
    window.onload = fetchTimerData;
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/data")
def get_data():
    with data_lock:
        current_data = latest_data
    return jsonify({"data": current_data})

@app.route("/timer")
def get_timer_info():
    with data_lock:
        return jsonify({
            "start": start_timestamp,
            "stop": stop_timestamp,
            "formatted": formatted_time
        })

@app.route('/simulate_button_press', methods=['POST'])
def simulate_button_press():
    try:
        ser_conn.write(b"GO\n")
        print("Simulated button press sent to Arduino.")
        return jsonify({"status": "success", "message": "Button press simulated"}), 200
    except Exception as e:
        print(f"Error sending button press: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_flask():
    app.run(host="0.0.0.0", port=5000)

# --- Main Execution ---
if __name__ == "__main__":
    ser_conn = connect_to_com_port(COM_PORT, BAUD_RATE, SERIAL_TIMEOUT)
    if not ser_conn:
        print("Exiting script since COM port connection was not established.")
        exit(1)

    reader_thread = threading.Thread(target=serial_read_thread, args=(ser_conn,), daemon=True)
    reader_thread.start()

    print("Starting Flask web server on http://0.0.0.0:5000")
    try:
        run_flask()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        ser_conn.close()
