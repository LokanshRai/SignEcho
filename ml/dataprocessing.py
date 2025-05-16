# %%
import re
import os
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d

def interpolate_2s(time, data, num_points=50):
    unique_indices = np.where(np.diff(time, prepend=np.nan) != 0)[0]
    time, data = time[unique_indices], data[unique_indices]
    
    time = time - time[0]  # Normalize time to start at 0
    interp_fn = interp1d(time, data, axis=0, fill_value='extrapolate')
    spaced_time = np.linspace(0, time[-1], num_points)
    return interp_fn(spaced_time)

def preprocess_dataset(dataset_dir):
    X, y = None, []
    for filename in os.listdir(dataset_dir):
        if not re.match(r'^[a-zA-Z]+_\d+__\d+\.csv$', filename):
            continue
        label = filename.split("_")[0]
        
        data = pd.read_csv(os.path.join(dataset_dir, filename))
        time = data['Time'].to_numpy()
        data = data[['Ang_X', 'Ang_Y', 'Ang_Z', 'Accel_X', 'Accel_Y', 'Accel_Z']].to_numpy()
        
        # Preprocess and interpolate data
        spaced_data = interpolate_2s(time, data)

        # import matplotlib.pyplot as plt

        # Plot each column of spaced_data in separate graphs
        # fig, axs = plt.subplots(6, 1, figsize=(10, 15))
        # columns = ['Ang_X', 'Ang_Y', 'Ang_Z', 'Accel_X', 'Accel_Y', 'Accel_Z']

        # for i in range(6):
        #     axs[i].plot(spaced_data[:, i])
        #     axs[i].set_title(columns[i])

        # plt.tight_layout()
        # plt.show()
        
        new_x = spaced_data.flatten().reshape(1, -1)
        if X is None:
            X = new_x
        else:
            X = np.vstack([X, new_x])
        y.append(label)
    
    return X, y

# %%
if __name__ == "__main__":
    dataset_dir = "C:\\Users\\basel\\OneDrive\\Desktop\\Waterloo\\1 UNI\\4FYDP\\signecho\\ml\\data\\Ritik_bassel_comp"
    X, y = preprocess_dataset(dataset_dir)

# %%