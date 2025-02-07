import matlab.engine
import numpy as np
import time

# Start MATLAB Engine
print("Starting MATLAB Engine...")
eng = matlab.engine.start_matlab()

# Change directory to the project path
project_path = r".\asbQuadcopter"
print(f"Changing MATLAB directory to: {project_path}")
eng.cd(project_path, nargout=0)

# Open the Simulink Project
project_file = "asbQuadcopter.prj"
print(f"Opening Simulink project: {project_file}")
eng.eval(f"openProject('{project_file}')", nargout=0)

# Open the Simulink Model
model_name = "asbQuadcopter"
print(f"Opening Simulink model: {model_name}")
eng.open_system(model_name, nargout=0)

# Define Simulation and Landing Parameters
sim_time = 20  # Total simulation time (seconds)
landing_time = 10  # Time when landing should begin
hover_altitude = 5  # Initial altitude (meters)
descent_rate = 0.5  # Meters per second descent rate

# Create time vector
print("Generating altitude command profile...")
t = np.linspace(0, sim_time, 100)
altitude_cmd = np.ones_like(t) * hover_altitude  # Hover initially

# Reduce altitude smoothly after landing time
landing_idx = np.where(t >= landing_time)[0][0]
altitude_cmd[landing_idx:] = np.linspace(
    hover_altitude, 0, len(altitude_cmd[landing_idx:])
)

# Convert to MATLAB format
t_matlab = matlab.double(t.tolist())
alt_cmd_matlab = matlab.double(altitude_cmd.tolist())

# Create MATLAB struct for Simulink input
print("Sending altitude command to MATLAB workspace...")
eng.workspace["AC_Command"] = {
    "time": t_matlab,
    "signals": {"values": alt_cmd_matlab, "dimensions": 1},
}

# Run Simulation
print(f"Starting simulation for {sim_time} seconds...")
eng.set_param(model_name, "SimulationCommand", "start", nargout=0)

# Monitor the simulation and modify altitude dynamically
while eng.get_param(model_name, "SimulationStatus") == "running":
    current_time = float(eng.get_param(model_name, "SimulationTime"))
    print(f"Simulation running... Time: {current_time:.2f}s")

    if current_time >= landing_time:
        new_altitude = max(0, hover_altitude - (current_time - landing_time) * descent_rate)
        eng.workspace["altitudeCmd"] = new_altitude  # Update altitude in MATLAB
        print(f"Descending... New altitude: {new_altitude:.2f} meters")

    time.sleep(0.1)  # Pause to avoid excessive calls

print("Simulation complete. Closing MATLAB Engine...")
eng.quit()
print("MATLAB Engine closed.")
