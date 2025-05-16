import asyncio
import csv
import time
from datetime import datetime
import struct
from bleak import BleakScanner, BleakClient

csv_filename = ""
LAST_SIGNED_INDEX = 240
SLEEP_TIME = 30

def get_nrf_device_identifier(name_filter="SignEcho"):
    """Scans for BLE devices and returns the address of the first matching device."""
    async def scan():
        for i in range(100):
            devices = await BleakScanner.discover()
            for device in devices:
                if name_filter in (device.name or ""):
                    print(f"Found device: {device.name} [{device.address}]")
                    return device.address
            print("No matching nRF device found.")
        return None
    
    return asyncio.run(scan())

async def notification_handler(sender, data):
    """Handles incoming BLE notifications."""
    # print(f"Received data from {sender}: {list(data)}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Keep only milliseconds

    # Convert bytes to a list of integers
    byte_values = list(data)

    combined_value = []

    for i in range(0, LAST_SIGNED_INDEX, 2):
        unsigned_val = (byte_values[i] << 8) | byte_values[i+1]
        combined_value.append(struct.unpack('>h', unsigned_val.to_bytes(2, 'big'))[0])

    for i in range(LAST_SIGNED_INDEX, len(byte_values), 2):
        combined_value.append((byte_values[i] << 8) | byte_values[i+1])

    # Append to CSV file
    with open(csv_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([timestamp] + combined_value)

async def connect_to_nrf(device_address, serv_id):
    """Connects to the nRF board using BLE, finds a specific service, and listens for messages."""
    if not device_address:
        print("No device address provided.")
        return
    
    async with BleakClient(device_address) as client:
        if await client.is_connected():
            print(f"Connected to {device_address}")
            services = await client.get_services()
            
            # Find the desired service
            target_service = None
            for service in services:
                if serv_id in service.uuid:
                    target_service = service
                    break
            
            if target_service:
                print(f"Found service: {target_service.uuid}")
                for characteristic in target_service.characteristics:
                    if "notify" in characteristic.properties:
                        print(f"Subscribing to characteristic {characteristic.uuid}")
                        await client.start_notify(characteristic.uuid, notification_handler)
                        await asyncio.sleep(SLEEP_TIME)  # Listen for 30 seconds
                        await client.stop_notify(characteristic.uuid)
            else:
                print("Service not found.")
        else:
            print("Failed to connect.")

if __name__ == "__main__":
    serv_id = "e9ea0001-e19b-482d-9293-c7907585fc48"  # Replace with the target service UUID
    # Write CSV headers (if the file is empty)
    curr_time = time.strftime("%Y_%m_%d_%H_%M_%S")
    csv_filename = f"BLEdata/trial_{curr_time}.csv"
    with open(csv_filename, "w", newline="") as file:
        writer = csv.writer(file)
        headers = ["Timestamp"] + [f"Value_{i}" for i in range(120)]
        writer.writerow(headers)
    device_address = get_nrf_device_identifier()
    if device_address:
        asyncio.run(connect_to_nrf(device_address, serv_id))