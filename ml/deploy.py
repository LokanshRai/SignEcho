import os
from ble.ble_reader import BLEReader
import pickle

ble_reader = BLEReader()


from app.app import Display
display = Display()
display.toggle_bluetooth()
display.render()

parent_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(parent_dir, "model/xgb.pkl"), "rb") as f:
    model = pickle.load(f)
with open(os.path.join(parent_dir, "model/label_encoder.pkl"), "rb") as f:
    label_encoder = pickle.load(f)

ble_reader.attach_display(display)
ble_reader.stream_data(model, label_encoder)
