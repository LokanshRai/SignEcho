# %%
file_name = "C:\\Users\\basel\\OneDrive\\Desktop\\Waterloo\\1 UNI\\4FYDP\\signecho\\ml\\data"

# %%
from ble.ble_reader import BLEReader

ble_reader = BLEReader()

# %%
ble_reader.collect_single_data_point("test_0", file_name, seconds=10)

# %%
import pandas as pd
import matplotlib.pyplot as plt

def plot_sensor_data(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Check if required columns are present
    required_columns = ["Time", "Ang_X", "Ang_Y", "Ang_Z", "Accel_X", "Accel_Y", "Accel_Z", "Rest"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError("CSV file does not contain the required columns")
    
    # Convert Time to numerical values if necessary
    df["Time"] = pd.to_numeric(df["Time"], errors='coerce')
    
    # Set min and max limits for Y-axis
    y_min, y_max = -32768, 32768
    
    # Create subplots
    fig, axes = plt.subplots(6, 1, figsize=(10, 12), sharex=True)
    
    # Plot each variable against Time
    for i, col in enumerate(["Ang_X", "Ang_Y", "Ang_Z", "Accel_X", "Accel_Y", "Accel_Z"]):
        axes[i].plot(df["Time"], df[col], label=col, color='b')
        axes[i].set_ylabel(col)
        axes[i].set_ylim(y_min, y_max)
        axes[i].legend()
        axes[i].grid()
        
        # Add transparent light red background where Rest is 1
        for j in range(len(df) - 1):
            if df["Rest"].iloc[j] == 1:
                axes[i].axvspan(df["Time"].iloc[j], df["Time"].iloc[j + 1], color='red', alpha=0.3)
    
    # Set x-axis label
    axes[-1].set_xlabel("Time")
    
    # Adjust layout
    plt.tight_layout()
    plt.show()

# Example usage
plot_sensor_data(file_name + "\\temp.csv")

# %%
