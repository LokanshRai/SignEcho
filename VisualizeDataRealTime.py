import os
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime as dt
import keyboard
import csv

s = serial.Serial(
    port= 'COM6',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=5
)
print("Connected to: " + s.portstr)

NUM_ADCS = 6
ADC_START_INDEX = 11
# SAMPLES = 1000
FOLDER_NAME = f"Data/Started_at_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

os.makedirs(FOLDER_NAME, exist_ok=True)

# adc = []
# for i in range(NUM_ADCS):
#     adc.append([])

x = []

def is_alphanumeric_pressed():
    for key in 'abcdefghijklmnopqrstuvwxyz':
        if keyboard.is_pressed(key):
            return key
    return None

# def write_to_csv():
#     f = open(f"DATA_{dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv", "x")
#     f.write("EMG1,EMG2,EMG3,EMG4,EMG5,EMG6\n")
#     for i in range(SAMPLES):
#         for j in range(NUM_ADCS):
#             f.write("%f," % adc[j][i])
#         f.write("\n")
#     f.close()

def save_to_csv(key, adc_data, timestamps):
    filename = os.path.join(FOLDER_NAME, f"{key}_{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "EMG1", "EMG2", "EMG3", "EMG4", "EMG5", "EMG6"])
        for time_stamp, row in zip(timestamps, zip(*adc_data)):
            writer.writerow([time_stamp] + list(row))
    print(f"Data saved to {filename}")

# This function is called periodically from FuncAnimation
def animate(i, xs, ys):

    try:
        data = s.readline().split()
        timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        for j in range(NUM_ADCS):
            while True:
                try:
                    adc[j].append(int(data[ADC_START_INDEX + j]))
                    break
                except:
                    data = s.readline().split()
                    pass
        timestamps.append(timestamp)
        # count += 1
    except Exception as e:
        print(f"Error: {e}")

    # Limit x and y lists to 20 items
    # timestamps = timestamps[-200:]
    # adc[0] = adc[0][-200:]

    # Draw x and y lists
    ax.clear()
    ax.plot(timestamps, adc[0])

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Live Feedback')
    plt.ylabel('Imu 1')

# for a in range(SAMPLES):
#     try:
#         data = s.readline().split()
#         for i in range(NUM_ADCS):
#             while True:
#                 try:
#                     adc[i].append(int(data[ADC_START_INDEX+i]))
#                     break
#                 except:
#                     data = s.readline().split()
#                     pass


#         x.append(count)
#         count += 1

#     except KeyboardInterrupt:
#         print("Closing: " + s.portstr)
#         break

# Create figure for plotting
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = []
ys = []
adc = [[] for _ in range(NUM_ADCS)]
timestamps = []
count = 0

# # Continuous loop to check for key press and collect data
# try:
#     while True:
#         key = is_alphanumeric_pressed()
#         if key:
#             print(f"Key '{key}' pressed. Collecting data...")
#             adc = [[] for _ in range(NUM_ADCS)]
#             timestamps = []
#             count = 0
#             while keyboard.is_pressed(key):
#                 try:
#                     data = s.readline().split()
#                     timestamp = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
#                     for i in range(NUM_ADCS):
#                         while True:
#                             try:
#                                 adc[i].append(int(data[ADC_START_INDEX + i]))
#                                 break
#                             except:
#                                 data = s.readline().split()
#                                 pass
#                     timestamps.append(timestamp)
#                     count += 1
#                 except Exception as e:
#                     print(f"Error: {e}")
#                     break
#             save_to_csv(key, adc, timestamps)
#             print(f"Key '{key}' released. Data collection stopped.")

# except KeyboardInterrupt:
#     print("Program interrupted. Closing connection.")
#     s.close()

# fig, ax = plt.subplots(6)  
# for i in range(NUM_ADCS):
#     ax[i].set_xlim([0, SAMPLES])
#     ax[i].set_ylim([0, 3300])
#     ax[i].plot(x, adc[i], label="Channel {}".format(i+1))
# plt.show()

# Set up plot to call animate() function periodically
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000, cache_frame_data=False)
plt.show()
