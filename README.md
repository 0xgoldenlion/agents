# Drone Sim

## Overview
This project simulates a quadcopter using MATLAB and Simulink. It integrates Python with MATLAB Engine to control the quadcopter's flight, including an automatic landing mechanism.

## Prerequisites
### Required Software:
- **MATLAB R2021a** 
- **Python 3.8 (64-bit)** (required for MATLAB Engine compatibility)

## Setup Instructions

### 1. Install Python 3.8 (64-bit)
Since MATLAB R2021a only supports Python 3.8 (64-bit), ensure you have it installed.

1. Download Python 3.8 (64-bit) from: [Python Releases](https://www.python.org/downloads/release/python-380/)
2. Install it and ensure it is available in your PATH.
3. Verify installation:
   ```sh
   py -3.8 --version
   ```

### 2. Install MATLAB Engine for Python

Run the following commands in **MATLAB Command Window**:

```sh
cd "C:\Program Files\MATLAB\R2021a\extern\engines\python"
py -3.8 setup.py install .
```

### 3. Install Python Dependencies
Run the following command to install required Python packages:
```sh
py -3.8 -m pip install numpy
```

### 4. fill evniroment variable 
In both Auto_approve and drone_web3 add `PRIVATE_KEY` and `OWNER_ADDRESS` 
```sh
PRIVATE_KEY = "YourPrivateKey"
OWNER_ADDRESS = "0xYourOwnerWallet"
```

### 5. Run auto approve script
Run the following command to run the approve script
```sh
py -3.8 auto_approve.py 
```


### 6. Run the Python Simulation Script
Run the script to start MATLAB, load the project, and control the quadcopter:
```sh
py -3.8 quad.py
```
