import FreeSimpleGUI as sg
import os
import pandas as pd
import openpyxl
import time
from datetime import datetime


def load_data_from_file(filename='Blood_Pressure_final.txt'):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            data = []
            for line in lines:
                if not line.strip():
                    continue
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) < 19:
                    continue

                # Only show summary in the table
                row = [
                    parts[0],       # Date
                    parts[10],      # Systolic Avg
                    parts[11],      # Diastolic Avg
                    parts[12],      # Pulse Avg
                    parts[13],      # Multi-Vitamin
                    parts[14],      # Telmisartan
                    parts[15],      # Amlodipine
                    parts[16],      # Rosuvastatin
                    parts[17],      # B-Complex
                    parts[18]       # Losartan
                ]
                data.append(row)
            return data
    except FileNotFoundError:
        return []


def get_current_datetime_info():
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    weekday_str = now.strftime("%A")
    full_now = now.strftime("%b %d %Y %H:%M:%S %A")
    return date_str, time_str, weekday_str, full_now

def check_bp_alerts(systolic, diastolic):
    if systolic >= 140 or diastolic >= 90:
        return "high"
    elif systolic <= 90 or diastolic <= 60:
        return "low"
    else:
        return "normal"

def export_to_excel(input_file='Blood_Pressure_final.txt', output_file='Blood_Pressure_export.xlsx'):
    try:
        headers = [
            'DateTime',
            'Systolic 1', 'Systolic 2', 'Systolic 3',
            'Diastolic 1', 'Diastolic 2', 'Diastolic 3',
            'Pulse 1', 'Pulse 2', 'Pulse 3',
            'Systolic Avg', 'Diastolic Avg', 'Pulse Avg',
            'Multi-Vitamin', 'Telmisartan', 'Amlodipine',
            'Rosuvastatin', 'B-Complex', 'Losartan'
        ]
        df = pd.read_csv(input_file, names=headers)
        df.to_excel(output_file, index=False)

        sg.popup('✅ Excel Export Successful', f'Saved as: {output_file}')
    except Exception as e:
        sg.popup_error('❌ Export Failed', str(e))












