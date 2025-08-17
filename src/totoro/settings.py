import os
import yaml


SETTINGS_FILE = os.path.join(os.getcwd(), 'totoro.yaml')

def load_settings():
    with open(SETTINGS_FILE, 'r') as f:
        return yaml.safe_load(f)