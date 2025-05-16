import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
file_path = 'BLEdata\\trial_2025_02_13_18_45_37.csv'
df = pd.read_csv(file_path)

# Extracting every 6th value from value_60 to value_119
columns_to_plot = [f'Value_{i}' for i in range(0, 59)]

# Create the figures for each shift but don't show them yet
figures = []
for shift in range(6):  # Create 6 plots, each with a 1-index shift
    # Shift the starting index
    sampled_data = df[columns_to_plot].iloc[shift:, ::6].values.flatten()
    
    # Create a new figure for each shift
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot the shifted data
    ax.plot(sampled_data, label=f'Shift {shift} (Start Index: {shift})')
    
    ax.set_title(f'Flattened Data from Every 6th Index (value_60 to value_119) - Shift {shift}')
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.legend()
    
    figures.append(fig)

# Show all figures at once
plt.show()
