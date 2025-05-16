# %%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import csv
import os
import pandas as pd
import struct
from datetime import datetime
from bleak import BleakScanner, BleakClient
from datetime import datetime
from collections import deque
from dataprocessing import interpolate_2s

# %%
class BLEReader:
    def __init__(self):
        self.serv_id = "e9ea0001-e19b-482d-9293-c7907585fc48" 
        # name = "SignEcho"
        name = "SignEchoNoEMG"
        self.device_address = self._get_nrf_device_identifier(name)
        self.ble_client, self.notify_characteristic = self._get_ble_client()

        self.last_tf_queue = deque()
        self.last_tf_queue_size = 10

        self.last_queue = [deque(), deque(), deque()]
        self.last_queue_size = 30

        self._output_dir = ""
        self._csv_filename = ""

        self._last_2_seconds = pd.DataFrame()
        self._last_2_seconds['Time'] = []
        self._last_2_seconds['Ang_X'] = []
        self._last_2_seconds['Ang_Y'] = []
        self._last_2_seconds['Ang_Z'] = []
        self._last_2_seconds['Accel_X'] = []
        self._last_2_seconds['Accel_Y'] = []
        self._last_2_seconds['Accel_Z'] = []

        self._prev_rest = False
        self._collection_state = False

        self.detections = 0
        self._display = None


    def __del__(self):
        """Destructor to ensure BLE client is properly disconnected."""
        if self.ble_client:
            print("Disconnecting BLE client...")
            asyncio.run(self._disconnect_client())

    async def _disconnect_client(self):
        try:
            if self.ble_client and await self.ble_client.is_connected():
                await self.ble_client.disconnect()
                print("BLE client disconnected.")
        except Exception as e:
            print(f"Error during disconnection: {e}")
    
    def _update_rest_tracker(self, data):
        for i in range(3):
            if len(self.last_queue[i]) >= self.last_queue_size:
                self.last_queue[i].popleft()
            self.last_queue[i].append(int(data[i]))
        
        is_rest = True
        for q in self.last_queue:
            s = 0
            for n in q:
                s += abs(n)
            if (s/len(q)) > 400:
                is_rest = False
                break
        
        if len(self.last_tf_queue) >= self.last_tf_queue_size:
            self.last_tf_queue.popleft()
        self.last_tf_queue.append(is_rest)

        rest_final = sum(self.last_tf_queue) >= self.last_tf_queue_size//2
        return rest_final

    def _get_nrf_device_identifier(self, name_filter="SignEchoNoEMG"):
        """Scans for BLE devices and returns the address of the first matching device."""
        print("Searching for device...")
        
        async def scan():
            for _ in range(100):
                devices = await BleakScanner.discover()
                for device in devices:
                    if name_filter == (device.name or ""):
                        print(f"Found device: {device.name} [{device.address}]")
                        return device.address
            raise Exception("No matching nRF device found.")
        
        return asyncio.run(scan())
    
    def _get_ble_client(self):
        """Attempts to establish a BLE connection with the discovered device."""
        if not self.device_address:
            raise Exception("No device address available.")
        
        async def connect():
            client = BleakClient(self.device_address)
            try:
                await client.connect()
                if await client.is_connected():
                    print(f"Connected to {self.device_address}")
                    services = await client.get_services()
                    
                    # Find the desired service and characteristic
                    for service in services:
                        if self.serv_id in service.uuid:
                            print(f"Found target service: {service.uuid}")
                            for characteristic in service.characteristics:
                                if "notify" in characteristic.properties:
                                    print(f"Found target characteristic: {characteristic.uuid}")
                                    return client, characteristic  # Return client and characteristic
                    
                    print("Target characteristic not found.")
                    await client.disconnect()
                    return None, None
            except Exception as e:
                print(f"Failed to connect: {e}")
                return None, None
            
            return None, None
        
        return asyncio.run(connect())

    async def _notification_handler(self, sender, data):

        """Handles incoming BLE notifications."""
        # print(f"Received data from {sender}: {list(data)}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Keep only milliseconds

        # Convert bytes to a list of integers
        byte_values = list(data)

        combined_value = []

        for i in range(0, 120, 2):
            unsigned_val = (byte_values[i] << 8) | byte_values[i+1]
            combined_value.append(struct.unpack('>h', unsigned_val.to_bytes(2, 'big'))[0])

        # Append to CSV file
        with open(self._csv_filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([timestamp] + combined_value)
        print("Data point received")
    
    def _collapse_csv(self):
        input_file = self._csv_filename  # Change this to your actual file path
        output_file = self._csv_filename

        with open(input_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = ["Time", "Ang_X", "Ang_Y", "Ang_Z", "Accel_X", "Accel_Y", "Accel_Z", "Rest"]
            expanded_rows = []
            
            first_timestamp = None
            for i, row in enumerate(reader):
                if first_timestamp is None:
                    first_timestamp = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                
                base_timestamp = datetime.strptime(row["Timestamp"], "%Y-%m-%d %H:%M:%S.%f")
                elapsed_time = (base_timestamp - first_timestamp).total_seconds()

                current_time = elapsed_time
                time_combined = f"{current_time:.6f}"

                xyz = [row[f"Ang_X_{9}"], row[f"Ang_Y_{9}"], row[f"Ang_Z_{9}"]]
                rest = self._update_rest_tracker(xyz)
                
                expanded_rows.append({
                    "Time": time_combined,
                    "Ang_X": row[f"Ang_X_{9}"],
                    "Ang_Y": row[f"Ang_Y_{9}"],
                    "Ang_Z": row[f"Ang_Z_{9}"],
                    "Accel_X": row[f"Accel_X_{9}"],
                    "Accel_Y": row[f"Accel_Y_{9}"],
                    "Accel_Z": row[f"Accel_Z_{9}"],
                    "Rest": rest
                })

        # Write to new CSV file
        if os.path.exists(output_file):
            os.remove(output_file)
        with open(output_file, mode='w+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expanded_rows)
    
    def _parse_data(self, label):
        input_file = self._csv_filename  # Path to input CSV file
        
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Check if required columns are present
        required_columns = ["Time", "Ang_X", "Ang_Y", "Ang_Z", "Accel_X", "Accel_Y", "Accel_Z", "Rest"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError("CSV file does not contain the required columns")

        # Convert Time to numerical values if necessary
        df["Time"] = pd.to_numeric(df["Time"], errors='coerce')

        # Detect transitions from Rest = 1 to Rest = 0
        df["Rest_Shift"] = df["Rest"].shift(1)  # Shifted Rest column
        transition_indices = df[(df["Rest_Shift"] == 1) & (df["Rest"] == 0)].index

        # Directory to save output files
        output_dir = self._output_dir
        os.makedirs(output_dir, exist_ok=True)
        for idx, transition_idx in enumerate(transition_indices):
            # Get the time of transition
            transition_time = df.loc[transition_idx, "Time"]

            # Define the time window: 0.2s before to 1.8s after
            start_time = transition_time - 0.2
            next_rest_idx = df[(df.index > transition_idx) & (df["Rest"] == 1)].index.min()
            if pd.notna(next_rest_idx):
                end_time = df.loc[next_rest_idx, "Time"]
            else:
                end_time = transition_time + 1.8  # Fallback in case no rest transition is found

            # Extract data within this time range
            extracted_data = df[(df["Time"] >= start_time) & (df["Time"] <= end_time)]

            # Generate a unique filename
            output_file = os.path.join(output_dir, f"{label}__{idx + 1}.csv")

            # Save the extracted data
            extracted_data.to_csv(output_file, index=False)

            print(f"Saved segment {idx + 1} to {output_file}")
    
    def collect_single_data_point(self, label, output_dir, seconds=10):
        """Collects a single data point from the BLE device."""
        timesteps_per_packet = 10
        self._output_dir = output_dir
        self._csv_filename = os.path.join(output_dir, "temp.csv")
        with open(self._csv_filename, "w+", newline="") as file:
            writer = csv.writer(file)
            headers = ["Timestamp"]
            for i in range(timesteps_per_packet):
                headers.append(f"Ang_X_{i}")
                headers.append(f"Ang_Y_{i}")
                headers.append(f"Ang_Z_{i}")
                headers.append(f"Accel_X_{i}")
                headers.append(f"Accel_Y_{i}")
                headers.append(f"Accel_Z_{i}")
            writer.writerow(headers)

        async def _collect_data():
            print("Starting Data Collect for 10 seconds...")
            await self.ble_client.start_notify(self.notify_characteristic.uuid, self._notification_handler)
            await asyncio.sleep(seconds)  # Listen for 30 seconds
            await self.ble_client.stop_notify(self.notify_characteristic.uuid)
            print("Data collect complete")

        asyncio.run(_collect_data())
        self._collapse_csv()
        self._parse_data(label)

    async def _stream_handler(self, sender, data):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        byte_values = list(data)
        combined_value = []
        for i in range(0, 120, 2):
            unsigned_val = (byte_values[i] << 8) | byte_values[i+1]
            combined_value.append(struct.unpack('>h', unsigned_val.to_bytes(2, 'big'))[0])
        
        ang_x = combined_value[-6]
        ang_y = combined_value[-5]
        ang_z = combined_value[-4]
        accel_x = combined_value[-3]
        accel_y = combined_value[-2]
        accel_z = combined_value[-1]
        new_data = {
            "Time": timestamp,
            "Ang_X": ang_x,
            "Ang_Y": ang_y,
            "Ang_Z": ang_z,
            "Accel_X": accel_x,
            "Accel_Y": accel_y,
            "Accel_Z": accel_z
        }
        
        self._last_2_seconds = self._last_2_seconds._append(new_data, ignore_index=True)

        xyz = [ang_x, ang_y, ang_z]
        rest = self._update_rest_tracker(xyz)
        
        if not self._collection_state:  
            # Keep only the last 0.2 seconds of data
            self._last_2_seconds = self._last_2_seconds[
                self._last_2_seconds["Time"].apply(lambda x: (datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")).total_seconds() <= 0.2)
            ]

            if rest == False and self._prev_rest == True:
                print("Starting collection")
                self._collection_state = True
        
        else:
            # first_point_time = datetime.strptime(self._last_2_seconds.iloc[0]["Time"], "%Y-%m-%d %H:%M:%S.%f")
            # current_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            # elapsed_time = (current_time - first_point_time).total_seconds()
            # if elapsed_time > 0.6 and rest == True:

            if rest and not self._prev_rest:
                print("Stopped collection")
                # Process the data
                datapoint = self._process_data()
                predicted = self.model.predict(datapoint)
                decoded_labels = self.label_encoder.inverse_transform(predicted)

                label = decoded_labels[0]
                print(f"Detection {self.detections}:\t{label}")
                self.detections += 1

                if self._display:
                    self._display.add_word(label)
                    self._display.render()

                self._collection_state = False

        self._prev_rest = rest   

    def _process_data(self):
        data = self._last_2_seconds[['Ang_X', 'Ang_Y', 'Ang_Z', 'Accel_X', 'Accel_Y', 'Accel_Z']].to_numpy()
        
        time = self._last_2_seconds["Time"]
        first_time = datetime.strptime(time.iloc[0], "%Y-%m-%d %H:%M:%S.%f")
        time = time.apply(lambda x: (datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") - first_time).total_seconds())
        time = time.to_numpy()

        data = interpolate_2s(time, data)
        data = data.flatten().reshape(1, -1)
        return data
    
    def stream_data(self, model, label_encoder):
        self.model = model
        self.label_encoder = label_encoder

        async def _collect_data():
            await self.ble_client.start_notify(self.notify_characteristic.uuid, self._stream_handler)
            await asyncio.sleep(9999999)
        asyncio.run(_collect_data())

    def attach_display(self, display):
        self._display = display