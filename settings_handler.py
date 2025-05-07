import json
import os
import PySimpleGUI as sg

SETTINGS_FILE = 'settings.json'

# Default settings
default_settings = {
    'theme': 'GreenTan',
    'unit': 'mmHg',
    'date_format': '%Y-%m-%d',
    'save_folder': './code/python/python_repository_files/'
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            sg.popup_error("Error reading settings.json. Using defaults.")
    return default_settings.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)
