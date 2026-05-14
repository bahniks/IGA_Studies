#! python3

import subprocess
import sys
import os
import time


temp_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp.json")
if os.path.exists(temp_json_path):
    os.remove(temp_json_path)

# Number of simultaneous instances to run
NUM_INSTANCES = 10

# Path to experiment.pyw (one directory up from current script)
experiment_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiment.pyw")

print(f"Starting {NUM_INSTANCES} simultaneous instances of experiment.pyw...")
print(f"Experiment path: {experiment_path}")

processes = []

try:
    # Start all instances simultaneously
    for i in range(1, NUM_INSTANCES + 1):
        print(f"Starting instance {i}/{NUM_INSTANCES}")
        
        command = [sys.executable, experiment_path,
                   "--load", "False"]

        # Use Popen to start process without waiting for it to finish
        process = subprocess.Popen(command, cwd=os.path.dirname(experiment_path))
        processes.append((i, process))
        
        # Small delay to avoid potential startup conflicts
        time.sleep(0.5)
    
    print(f"\nAll {NUM_INSTANCES} instances started successfully!")
    print("Each instance is running independently.")
    print("Close each application window manually when finished.")
    
    # Optional: Wait for all processes to complete
    print("\nWaiting for all instances to finish...")
    for instance_num, process in processes:
        process.wait()  # Wait for this process to complete
        print(f"Instance {instance_num} finished")
    
    print("All instances completed!")

except KeyboardInterrupt:
    print("\nTerminating all instances...")
    for instance_num, process in processes:
        try:
            process.terminate()
            print(f"Instance {instance_num} terminated")
        except:
            pass
    print("All instances terminated.")

except Exception as e:
    print(f"Error starting instances: {e}")
    # Cleanup any started processes
    for instance_num, process in processes:
        try:
            process.terminate()
        except:
            pass
