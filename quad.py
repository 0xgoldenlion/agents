import matlab.engine
import numpy as np
import time
from drone_web3 import request_landing, wait_for_landing_approval

def log_event(message):
    """Prints and logs events in the simulation."""
    print(f"[EVENT] {time.strftime('%H:%M:%S')} - {message}")

# Start MATLAB Engine
log_event("Starting MATLAB Engine...")
eng = matlab.engine.start_matlab()

# Open the Simulink Project
project_path = r".\asbQuadcopter"
log_event(f"Changing MATLAB directory to: {project_path}")
eng.cd(project_path, nargout=0)

log_event("Opening Simulink project: asbQuadcopter.prj")
eng.eval("openProject('asbQuadcopter.prj')", nargout=0)

# Get the actual model name dynamically
model_name = eng.bdroot()
log_event(f"Detected Simulink Model: {model_name}")
eng.open_system(model_name, nargout=0)

# Compile the model to ensure settings apply
log_event("Compiling Simulink model...")
eng.set_param(model_name, "SimulationCommand", "update", nargout=0)

# Set simulation StopTime
sim_time = 300  # Enough time to hover and land
log_event(f"Setting simulation StopTime to {sim_time}s...")
eng.set_param(model_name, "StopTime", str(sim_time), nargout=0)

# Attempt to read initial altitude from the third element of States.LLA
try:
    # Using eng.eval(...) is often the simplest robust approach
    initial_altitude = float(eng.eval("States.LLA(3)", nargout=1))
    log_event(f"Initial altitude detected: {initial_altitude:.2f}m")
except:
    log_event("Warning: Failed to read initial altitude! Using fallback value...")
    initial_altitude = 5.0  # Fallback

# Prepare MATLAB struct for Command (read existing Command from workspace, then modify)
try:
    # Get the existing struct from base workspace
    command_struct = eng.workspace['Command']
except KeyError:
    # If 'Command' does not exist, create a blank struct with at least an 'altitude' field
    command_struct = {
        'yawStepAmplitude': 0.0,
        'yawStepTime': 0.0,
        'yawStepDuration': 0.0,
        'pitchStepAmplitude': 0.0,
        'pitchStepTime': 0.0,
        'pitchStepDuration': 0.0,
        'rollStepAmplitude': 0.0,
        'rollStepTime': 0.0,
        'rollStepDuration': 0.0,
        'takeoffDuration': 1.0,
        'altitude': 0.0,  # <- important
        'rollDeadZoneEnd': 0.5,
        'rollDeadZoneStart': -0.5,
        'rollSatUpper': 1.0,
        'rollSatLower': -1.0,
        'rollGain': 1.0,
        'pitchDeadZoneEnd': 0.5,
        'pitchDeadZoneStart': -0.5,
        'pitchSatUpper': 1.0,
        'pitchSatLower': -1.0,
        'pitchGain': 1.0,
        'yawDeadZoneEnd': 0.5,
        'yawDeadZoneStart': -0.5,
        'yawSatUpper': 1.0,
        'yawSatLower': -1.0,
        'yawGain': 1.0
    }

# Set initial hover altitude
hover_altitude = initial_altitude
landing_altitude = 0.0  # We want to come down to ~0 AGL (depending on how your model interprets altitude)
command_struct['altitude'] = hover_altitude

# Push the updated command_struct to base workspace
eng.workspace['Command'] = command_struct
eng.eval("assignin('base','Command', Command);", nargout=0)

# Start simulation
log_event("Starting MATLAB simulation...")
eng.set_param(model_name, "SimulationCommand", "start", nargout=0)

eng.eval("VSS_COMMAND = 0;", nargout=0)
eng.set_param(model_name, "SimulationCommand", "update", nargout=0)

eng.eval("enableLanding = true;", nargout=0)
eng.eval("landingAltitude = 0;", nargout=0)  # or whatever the model expects

command_struct['takeoffDuration'] = 0.0
eng.workspace['Command'] = command_struct
eng.eval("assignin('base','Command', Command);", nargout=0)


# Step 2: Request Landing Approval (via your blockchain logic)
log_event("Requesting landing approval from blockchain...")
request_landing()

log_event("Waiting for landing approval...")
landing_zone = wait_for_landing_approval()
log_event(f"Landing Approved in zone: {landing_zone}")

# Step 3: Landing loop
landing_time = float(eng.get_param(model_name, "SimulationTime"))
log_event(f"Landing will start at simulation time: {landing_time:.2f}s")

log_event("Updating altitude command to initiate landing...")

while True:
    sim_status = eng.get_param(model_name, "SimulationStatus")
    current_time = float(eng.get_param(model_name, "SimulationTime"))

    # Safely read real-time altitude from States.LLA(3)
    try:
        altitude = float(eng.eval("States.LLA(3)", nargout=1))
    except:
        log_event("Warning: Could not read States.LLA(3)! Using fallback altitude.")
        altitude = hover_altitude

    # Check if we've reached the time to descend
    if current_time >= landing_time:
        if altitude > 0.1:
            # Decrease altitude setpoint gradually
            hover_altitude -= 0.1
            if hover_altitude < landing_altitude:
                hover_altitude = landing_altitude

            # Update Command.altitude in MATLAB
            command_struct['altitude'] = hover_altitude
            eng.workspace['Command'] = command_struct
            eng.eval("assignin('base','Command', Command);", nargout=0)

            log_event(f"Descending... Setpoint: {hover_altitude:.2f}m | Actual: {altitude:.2f}m")
        else:
            log_event("Drone has landed successfully.")
            break

    # If simulation stops unexpectedly, restart it
    if sim_status != "running":
        log_event("Simulation stopped unexpectedly! Restarting it now...")
        eng.set_param(model_name, "SimulationCommand", "start", nargout=0)

    time.sleep(0.1)

# Step 5: Shutdown
log_event("Landing completed. Closing MATLAB Engine...")
eng.quit()
log_event("MATLAB Engine closed.")
