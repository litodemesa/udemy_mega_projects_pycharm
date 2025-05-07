import FreeSimpleGUI as sg
import pandas as pd


def build_medicine_checkboxes(med_list):
    return [[sg.Checkbox(med, key=f'-MED-{med}-')] for med in med_list]


def build_main_layout(med_list):
    return [
        [sg.B("Manage Medicines")],
        [sg.Frame("Today's Medicines", build_medicine_checkboxes(med_list), key='-MED_FRAME-')],
        [sg.B('Save'), sg.B('Exit')]
    ]

def manage_medicines(med_list):
    layout = [
        [sg.Text("Current Medicines:")],
        [sg.Listbox(values=med_list, key='-MEDLIST-', size=(40, 5))],
        [sg.Text("New or Updated Entry:"), sg.Input(key='-MEDINPUT-')],
        [sg.Button("Add/Update"), sg.Button("Remove"), sg.Button("Close")]
    ]
    window = sg.Window("Manage Medicines", layout, modal=True)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Close"):
            break
        elif event == "Add/Update":
            med = values['-MEDINPUT-']
            if med:
                if med not in med_list:
                    med_list.append(med)
                    build_medicine_checkboxes(med_list)
                    build_main_layout(med_list)
                    window['-MEDLIST-'].update(values=med_list)
                else:
                    index = med_list.index(med)
                    med_list[index] = med
                window['-MEDLIST-'].update(med_list)
        elif event == "Remove":
            selected = values['-MEDLIST-']
            if selected:
                med_list.remove(selected[0])
                window['-MEDLIST-'].update(med_list)
    window.close()
    # return med_list


# Function to show data summary
def show_summary(data_frame):
    """
    Display a summary report of blood pressure data.

    Args:
        data_frame (pd.DataFrame): DataFrame containing blood pressure data
    """
    if not isinstance(data_frame, pd.DataFrame) or data_frame.empty:
        sg.popup_error("No data to summarize!")
        return

    summary = f"""
    Blood Pressure Summary Report:
    -----------------------------
    Total Records: {len(data_frame)}
    Average Systolic: {data_frame['Systolic'].mean():.1f} mmHg
    Average Diastolic: {data_frame['Diastolic'].mean():.1f} mmHg
    Average Pulse: {data_frame['Pulse'].mean():.1f} BPM

    Normal BP Records: {len(data_frame[(data_frame['Systolic'] < 140) & (data_frame['Diastolic'] < 90)])}
    Elevated BP Records: {len(data_frame[(data_frame['Systolic'] >= 140) | (data_frame['Diastolic'] >= 90)])}
    """

    sg.popup_scrolled(summary, title="BP Summary Report", size=(60, 15))


# Function to detect anomalies in BP readings
def detect_anomalies(data_frame):
    """
    Identify and display anomalous blood pressure readings.

    Args:
        data_frame (pd.DataFrame): DataFrame containing blood pressure data
    """
    if not isinstance(data_frame, pd.DataFrame) or data_frame.empty:
        sg.popup_error("No data to analyze!")
        return

    # Simple anomaly detection - readings that differ significantly from average
    mean_sys = data_frame['Systolic'].mean()
    mean_dia = data_frame['Diastolic'].mean()
    std_sys = data_frame['Systolic'].std()
    std_dia = data_frame['Diastolic'].std()

    # Mark readings as anomalies if they are more than 2 standard deviations from the mean
    anomalies = data_frame[
        (data_frame['Systolic'] > mean_sys + 2 * std_sys) |
        (data_frame['Systolic'] < mean_sys - 2 * std_sys) |
        (data_frame['Diastolic'] > mean_dia + 2 * std_dia) |
        (data_frame['Diastolic'] < mean_dia - 2 * std_dia)
        ]

    if anomalies.empty:
        sg.popup("No significant anomalies detected in your BP readings.")
        return

    # Format the anomalies for display
    anomaly_text = "Potential anomalies detected in these readings:\n\n"
    for idx, row in anomalies.iterrows():
        anomaly_text += f"Date: {row['Date']}, BP: {row['Systolic']}/{row['Diastolic']}\n"

    sg.popup_scrolled(anomaly_text, title="Anomaly Detection", size=(60, 15))

def about():
    about_text = """
                   Blood Pressure Tracker Application
                   --------------------------------
                   Version 1.0

                   A comprehensive tool for monitoring and analyzing blood pressure readings.

                   Made with ❤️ using PySimpleGUI

                   © 2025 BP Tracker Team
                   Author: Tholits De Mesa Email: rbdemesa47@gmail.com
                   """
    sg.popup_scrolled(about_text, title='About Blood Pressure Tracker', size=(70, 15))
