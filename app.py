from flask import Flask, render_template, jsonify
from sense_hat import SenseHat
import time
import math
from threading import Thread

# Initialize Flask app and Sense HAT
app = Flask(__name__)
sense = SenseHat()

# Constants for controlling the speedometer's behavior
UPDATE_INTERVAL = 0.1  # Time interval (in seconds) between velocity updates
SCALE_FACTOR = 0.5     # Factor to scale the calculated velocity (adjust for readability)
METER_TO_KMH = 3.6     # Conversion factor from m/s to km/h

# Global variable to store the current velocity
velocity_kmh = 0

def calculate_velocity(accel_data, delta_time):
    """
    Calculate velocity based on acceleration data and time interval.
    
    Parameters:
    accel_data: Tuple containing acceleration values (ax, ay, az) in g's.
    delta_time: Time interval over which the velocity is calculated.

    Returns:
    Calculated velocity based on the input acceleration and time.
    """
    ax, ay, az = accel_data  # Extract acceleration components

    # Integrate acceleration to calculate velocity in each direction
    velocity_x = ax * delta_time
    velocity_y = ay * delta_time
    velocity_z = az * delta_time

    # Calculate the resultant velocity (magnitude of the velocity vector)
    return math.sqrt(velocity_x**2 + velocity_y**2 + velocity_z**2)

def update_velocity():
    """
    Continuously update the velocity by reading acceleration data from the Sense HAT.
    This function runs in a separate thread.
    """
    global velocity_kmh
    last_time = time.time()  # Record the current time to calculate time intervals

    while True:
        current_time = time.time()  # Get the current time
        delta_time = current_time - last_time  # Calculate time interval since last update

        # Get raw accelerometer data from the Sense HAT (returns a dictionary with x, y, z keys)
        accel_data = sense.get_accelerometer_raw().values()

        # Calculate velocity in m/s based on the acceleration data and time interval
        velocity_mps = calculate_velocity(accel_data, delta_time) * SCALE_FACTOR

        # Convert the velocity from m/s to km/h
        velocity_kmh = velocity_mps * METER_TO_KMH

        # Update the last_time variable for the next iteration
        last_time = current_time

        # Pause for the update interval to control how often velocity is recalculated
        time.sleep(UPDATE_INTERVAL)

@app.route('/')
def index():
    """
    Serve the main page (index.html) which displays the speedometer.
    """
    return render_template('index.html')

@app.route('/speed')
def get_speed():
    """
    Provide the current speed as a JSON response. This endpoint is used by the frontend
    to fetch the latest speed data asynchronously.
    
    Returns:
    JSON object containing the current speed in km/h.
    """
    return jsonify(speed=round(velocity_kmh, 2))  # Round the velocity to 2 decimal places for readability

if __name__ == "__main__":
    # Start the velocity update function in a separate thread
    velocity_thread = Thread(target=update_velocity)
    velocity_thread.start()

    # Run the Flask app on the Raspberry Pi, accessible from other devices on the network
    app.run(host='0.0.0.0', port=5000)
