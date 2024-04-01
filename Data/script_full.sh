#!/bin/bash

# Set the path to your Python script
python_script="./scrape_full.py"

# Function to check if the Python script is running
is_python_running() {
    pgrep -f "$python_script"
}

# Function to run the Python script
run_python_script() {
    echo "Running Python script..."
    python3 "$python_script" 
}

# Infinite loop to check and run the Python script if not running
while true; do
    if is_python_running; then
        echo "Python script is already running."
    else
        run_python_script
    fi

    # Adjust the sleep duration based on how frequently you want to check
    sleep 20
done
