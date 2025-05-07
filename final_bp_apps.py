# YOU ARE HERE EDITING -
import FreeSimpleGUI as sg
import pandas as pd
from datetime import datetime
import json
import os
import glob
import threading
import datetime
import time
from bp_load_functions import * # Ensure this is implemented properly or remove if unused.
from bp_helper_function1 import *
from settings_handler import load_settings, save_settings
from dialogs import (
    show_theme_selector,
    choose_unit,
    choose_date_format,
    choose_save_folder
)
from tool_functions import *
from weather_apps import show_weather_window
from calculator import calculate
from bmi import bmi_calculation
from BP_Category import *
from bp_med_reminders import reminder_loop
from medicine_dashboard import medicine_dashboard_tracker
# --- GUI Setup ---

sg.set_options(font=('Roboto Mono', 12))
full_row_data = []
selected_row_index = None
filename = "Blood_Pressure_final.txt"
csv_repo = "c:/users/rizal/Documents/Blood_Pressure_Project/csv_folder/"  # update this with your actual path
list_of_csv = glob.glob(os.path.join(csv_repo, "*.csv"))
if list_of_csv:
    latest_csv = max(list_of_csv, key=os.path.getctime)
    df = pd.read_csv(latest_csv)
else:
    sg.popup("No CSV file found", title="Warning")
    latest_csv = None


"""
Blood Pressure Tracker Application
----------------------------------
A comprehensive blood pressure tracking application with data visualization,
medication tracking, and health alerts.

Features:
- Record and track multiple blood pressure readings
- Calculate averages and detect potential health issues
- Track medication compliance
- Generate charts and export data for analysis
- Customizable settings for units and date formats
"""

def create_window():
    """
       Create the main application window with all UI elements properly configured.

       Returns:
           sg.Window: The configured PySimpleGUI main application window
       """
    menu_def = [
        ['&File', ['&Save', '&Update', '---', 'E&xit']],
        ['&View', ['&Preview Data Table', '&Export to Excel', '&Convert to CSV', '&Update Table Data']],
        ['&Charts', [
            'Weekly', ['Weekly Line Chart', 'Weekly Bar Chart'],
            'Monthly', ['Monthly Line Chart', 'Monthly Bar Chart']
        ]],
        ['Tools', ['Add/Edit Medicines','Blood Pressure Category', 'BMI Calculator', 'Calculator', 'Detect Anomalies', 'Show Summary', '&Weather']],
        ['&Setting', ['Change Theme', 'Set Save Folder', 'Set Unit', 'Set Date Format']],
        ['&Help', ['&About']]
    ]

    toprow = ['Date', 'Systolic', 'Diastolic Avg', 'Pulse Avg',
              'M-Vit', 'Telmisartan', 'Amlodipine',
              'Rosuvastatin', 'B-Complex', 'Losartan']

    # --Layout design--

    # Row 1: Timestamp, Day, Date, Time
    timestamp_row = [
        [sg.Text('Timestamp:'), sg.Text('', key='-NOW-', size=(40, 1))],
        [sg.Text('Date (YYYY-MM-DD):', size=(20, 1)),sg.Input(key='date', size=(12,1))],
        [sg.Text('Time (HH:MM):', size=(20, 1)), sg.Input(key='hm', size=(8, 1))],
        [sg.Text('Day', size=(20, 1)), sg.Input(key='day', size=(12, 1))]
    ]

    # Row 2: Medicine Checkboxes

    med_row1 = [
        sg.Checkbox('Multi-Vitamin', default=False, key='-MED1-', enable_events=True),
        sg.Checkbox('Telmisartan', default=False, key='-MED2-', enable_events=True),
        sg.Checkbox('Amlodipine', default=False, key='-MED3-', enable_events=True)]
    med_row2 = [
        sg.Checkbox('Rosuvastatin', default=False, key='-MED4-', enable_events=True),
        sg.Checkbox('B-Complex', default=False, key='-MED5-', enable_events=True),
        sg.Checkbox('Losartan', default=False, key='-MED6-', enable_events=True)]

    med_row3 = [
        sg.B('Medicine Dashboard'),

    ]


    clo = sg.Frame('Medicine Taken', [med_row1, med_row2, med_row3], title_color='blue')
    col1 = [
        [clo]
    ]


    # Row 3: Blood Pressure Readings
    # Row 3: Blood Pressure Readings
    readings_frame = sg.Frame('Blood Pressure Readings', [
        [sg.Text('First Reading:', size=(17, 1)),sg.Push(), sg.Input(size=(10,1), key='s_21'), sg.Input(size=(10,1), key='d_31'), sg.Input(size=(10,1), key='p_41'), sg.Push()],
        [sg.Text('Second Reading:', size=(17, 1)), sg.Push(), sg.Input(size=(10,1), key='s_22'), sg.Input(size=(10,1), key='d_32'), sg.Input(size=(10,1), key='p_42'), sg.Push()],
        [sg.Text('Third Reading:', size=(17, 1)), sg.Push(), sg.Input(size=(10,1), key='s_23'), sg.Input(size=(10,1), key='d_33'), sg.Input(size=(10,1), key='p_43'), sg.Push()],
        [sg.Text('Average Reading:'), sg.Push(),sg.Text('',size=(10,1), key='systolic'), sg.Text('', size=(10,1), key='diastolic'), sg.Text('', size=(10,1), key='pulse'), sg.Push()],
        [sg.Text("", key='-result-')]
    ])
    col2 = [
        [readings_frame]
    ]

    # Row 4: Actions - Split into two frames
    data_actions = sg.Frame('📄 Data Actions', [
        [sg.Button('Preview Data Table', key='-PREVIEW-'),sg.Button('Export to Excel',key="-excel-")],
        [sg.Button('Convert to CSV', key='-csv-'), sg.Button("Update Data Table", key='-UPDATE-')]
    ])
    col3 = [[data_actions]]
    chart_actions = sg.Frame('📈 Chart Actions', [
        [sg.Button('Weekly Line Chart', key='-WEEKLY-LINE-'),sg.Button('Weekly Bar Chart', key='-WEEKLY-BAR-'),],
        [sg.Button('Monthly Line Chart', key='-MONTHLY-LINE-'),sg.Button('Monthly Bar Chart', key='-MONTHLY-BAR-')]
    ])
    col4 = [[chart_actions]]
    # Row 5: Save / Edit Buttons
    action_buttons = [
        sg.Button('Save Entry', key="-SAVE-", button_color=('white', 'green')),
        sg.Button('Edit Selected Row', key='-EDIT-', button_color=('white', 'firebrick3')),
        sg.B('Delete Selected', key='-DELETE-'),
        sg.Button('Exit', key='-EXIT-', button_color=('white', 'tomato'))
    ]

    # Row 6: Data Table
    data_table_frame = sg.Frame('📋 Data Table Preview', [
        [sg.Table(
            headings=['Date', 'Systolic Avg', 'Diastolic Avg', 'Pulse Avg', 'M-Vit', 'Telmisartan', 'Amlodipine', 'Rosuvastatin', 'B-Complex'],
            values=[],
            key='TABLE',
            auto_size_columns=False,
            justification='center',
            selected_row_colors="yellow on green",
            num_rows=7,
            enable_events=True,
            vertical_scroll_only=False,
            col_widths=[12, 10, 10, 8, 8, 10, 10, 10, 10]
        )]
    ])
    # --- Final Layout Assembly ---
    layout = [
        [sg.Menu(menu_def)],
        [sg.Text('🩺 Blood Pressure Tracker', font=('Helvetica', 20, 'bold'), justification='center', expand_x=True)],
        [sg.Column(timestamp_row)],
        [sg.HorizontalSeparator()],
        [sg.Col(col1), sg.VerticalSeparator(), sg.Col(col2)],
        [sg.HorizontalSeparator()],
        [sg.Text("", key='-EDIT-STATUS-', text_color='green', size=(50, 1))],
        [sg.Col(col3,justification='center'), sg.VerticalSeparator(), sg.Col(col4, justification='center')],
        [sg.HorizontalSeparator()],
        [sg.Column([action_buttons], justification='center')],
        [data_table_frame]

    ]

    tbl1 = sg.Table(
        values=full_row_data,
        headings=toprow,
        justification='center',
        auto_size_columns=False,
        col_widths=[12] * len(toprow),
        num_rows=10,
        expand_x=True,
        expand_y=True,
        selected_row_colors="yellow on green",
        enable_events=True,
        enable_click_events=True,
        key='TABLE',
        vertical_scroll_only=False) # <-- This is important to allow both scrollbars

    # --- Window ---
    return sg.Window('Blood Pressure Tracker 🩺', layout, size=(1000, 750), finalize=True, resizable=True)


def main():
    global selected_row_index, editing_index
    unit = 'mmHg'
    date_format = '%Y-%m-%d'
    from datetime import datetime
    now = datetime.now().strftime(date_format)

    medicine_list = ['M-Vit', 'Telmisartan', 'Amlodipine', 'Rosuvastatin', 'B-Complex', 'Losartan']
    settings = load_settings()
    sg.theme(settings['theme'])
    window = create_window()
    # bp_times = ['07:30', '20:00']  # e.g., BP reminders
    # med_times = ['08:00', '21:00']  # e.g., medicine reminders
    now = datetime.now()
    test_time = (now + timedelta(minutes=1)).strftime('%H:%M')

    bp_times = [test_time]
    med_times = [test_time]

    threading.Thread(target=reminder_loop, args=(window, bp_times, med_times), daemon=True).start()



    # --- Event Loop ---
    while True:
        event, values = window.read(timeout=2000)
        # print(event)
        # print(values)


        if event in (sg.WIN_CLOSED, 'Cancel', 'Exit'):
            break


        date_str, time_str, weekday_str, full_now = get_current_datetime_info()
        window['-NOW-'].update(full_now)

        match event:
            case 'Calculator':
                calculate()

            case  "Manage Medicines":
                new_med_list = manage_medicines(medicine_list.copy())  # get updated list
                if new_med_list != medicine_list:
                    medicine_list = new_med_list  # update global list
                    # 🔄 Rebuild the checkbox section
                    window['-MED_FRAME-'].update(build_medicine_checkboxes(medicine_list))

            case '-EDIT-':
                if 'TABLE' in values and values['TABLE']:
                    try:
                        selected_row_index = values['TABLE'][0]
                        parts = full_row_data[selected_row_index]

                        # Load timestamp and parse date/time
                        # window['-NOW-'].update(full_now)
                        date_time_str = parts[0] # First column
                        from datetime import datetime
                        try:
                            dt = datetime.strptime(date_time_str, "%b %d %Y %H:%M:%S %A")
                            window['date'].update(dt.strftime("%Y-%m-%d"))
                            window['hm'].update(dt.strftime("%H:%M"))
                            window['day'].update(dt.strftime("%A"))
                        except ValueError:
                            print("Invalid date format in row: ", date_time_str)

                        window['s_21'].update(parts[1])
                        window['s_22'].update(parts[2])
                        window['s_23'].update(parts[3])
                        window['d_31'].update(parts[4])
                        window['d_32'].update(parts[5])
                        window['d_33'].update(parts[6])
                        window['p_41'].update(parts[7])
                        window['p_42'].update(parts[8])
                        window['p_43'].update(parts[9])

                        # Calculate and update averages
                        systolic_avg = round((int(parts[1]) + int(parts[2]) + int(parts[3])) / 3)
                        diastolic_avg = round((int(parts[4]) + int(parts[5]) + int(parts[6])) / 3)
                        pulse_avg = round((int(parts[7]) + int(parts[8]) + int(parts[9])) / 3)

                        category = classify_bp(systolic_avg, diastolic_avg)

                        window['systolic'].update(f"{systolic_avg}")
                        window['diastolic'].update(f"{diastolic_avg}")
                        window['pulse'].update(f"{pulse_avg}")
                        window['-result-'].update(f"Result: {systolic_avg}/{diastolic_avg} {unit}  Pulse -> {pulse_avg} Category: {category}", text_color='blue')

                        # Update checkboxes based on table positions (index in full_row_data matches table)
                        # Medicine fields start at index 13 in the full data structure
                        window['-MED1-'].update(parts[13] == 'Yes')
                        window['-MED2-'].update(parts[14] == 'Yes')
                        window['-MED3-'].update(parts[15] == 'Yes')
                        window['-MED4-'].update(parts[16] == 'Yes')
                        window['-MED5-'].update(parts[17] == 'Yes')
                        window['-MED6-'].update(parts[18] == 'Yes')

                        # Update status message
                        window['-EDIT-STATUS-'].update("Now editing selected record. Press Update to save changes.")
                    except Exception as e:
                        sg.popup_error(f"Error loading data for editing: {str(e)}")
                else:
                    sg.popup_error("Please select a row to edit first.")

            case '-DELETE-':
                if 'TABLE' in values and values['TABLE']:
                    try:
                        selected_row_index = values['TABLE'][0]

                        confirm = sg.popup_yes_no("Are you sure you want to delete the selected row?")
                        if confirm == 'Yes':
                            # Remove the selected row
                            del full_row_data[selected_row_index]

                            # Update the table
                            window['TABLE'].update(values=full_row_data)

                            # Optionally clear form fields
                            window['date'].update('')
                            window['hm'].update('')
                            window['s_21'].update('')
                            window['s_22'].update('')
                            window['s_23'].update('')
                            window['d_31'].update('')
                            window['d_32'].update('')
                            window['d_33'].update('')
                            window['p_41'].update('')
                            window['p_42'].update('')
                            window['p_43'].update('')
                            window['systolic'].update('')
                            window['diastolic'].update('')
                            window['pulse'].update('')
                            window['-result-'].update('Result: ')
                            for i in range(1, 7):
                                window[f'-MED{i}-'].update(False)
                            window['-EDIT-STATUS-'].update("Record deleted successfully.")
                    except Exception as e:
                        sg.popup_error(f"Error deleting row: {str(e)}")
                else:
                    sg.popup_error("Please select a row to delete first.")

            case 'Preview Data Table' | '-PREVIEW-':
                with open(filename, 'r') as f:
                    full_row_data.clear()
                    lines = f.readlines()
                    rows = []
                    for line in lines:
                        parts = [p.strip() for p in line.strip().split(',')]
                        if len(parts) < 19:
                            continue
                        full_row_data.append(parts)
                        rows.append([
                            parts[0], parts[10], parts[11], parts[12],
                            parts[13], parts[14], parts[15],
                            parts[16], parts[17], parts[18]
                        ])
                    window['TABLE'].update(values=rows)

            case 'Update' | '-UPDATE-':
                if selected_row_index is not None:
                    try:
                        # Validate inputs
                        try:
                            # Make sure all fields have values before converting to int
                            if not all([values['s_21'], values['s_22'], values['s_23'],
                                       values['d_31'], values['d_32'], values['d_33'],
                                       values['p_41'], values['p_42'], values['p_43']]):
                                sg.popup_error("All reading fields must be filled.")
                                continue

                            s1 = int(values['s_21'])
                            s2 = int(values['s_22'])
                            s3 = int(values['s_23'])
                            d1 = int(values['d_31'])
                            d2 = int(values['d_32'])
                            d3 = int(values['d_33'])
                            p1 = int(values['p_41'])
                            p2 = int(values['p_42'])
                            p3 = int(values['p_43'])

                            # Validate blood pressure ranges with more detailed error messages
                            systolic_ranges = [50 <= val <= 250 for val in (s1, s2, s3)]
                            if not all(systolic_ranges):
                                invalid_indices = [i+1 for i, valid in enumerate(systolic_ranges) if not valid]
                                sg.popup_error(f"Systolic reading(s) {', '.join(map(str, invalid_indices))} should be between 50 and 250.")
                                continue

                            diastolic_ranges = [30 <= val <= 150 for val in (d1, d2, d3)]
                            if not all(diastolic_ranges):
                                invalid_indices = [i+1 for i, valid in enumerate(diastolic_ranges) if not valid]
                                sg.popup_error(f"Diastolic reading(s) {', '.join(map(str, invalid_indices))} should be between 30 and 150.")
                                continue

                            pulse_ranges = [40 <= val <= 180 for val in (p1, p2, p3)]
                            if not all(pulse_ranges):
                                invalid_indices = [i+1 for i, valid in enumerate(pulse_ranges) if not valid]
                                sg.popup_error(f"Pulse reading(s) {', '.join(map(str, invalid_indices))} should be between 40 and 180.")
                                continue
                        except ValueError:
                            sg.popup_error("All readings must be valid numbers.")
                            continue

                        # Calculate averages
                        systolic_avg = round((s1 + s2 + s3) / 3)
                        diastolic_avg = round((d1 + d2 + d3) / 3)
                        pulse_avg = round((p1 + p2 + p3) / 3)

                        with open( 'r') as file:
                            lines = file.readlines()

                        selected_row_index = values['TABLE'][0]
                        parts = full_row_data[selected_row_index]

                        # New edited line
                        new_line = (
                            f"{values['parts']},"
                            f"{s1},{s2},{s3},"
                            f"{d1},{d2},{d3},"
                            f"{p1},{p2},{p3},"
                            f"{systolic_avg},{diastolic_avg},{pulse_avg},"
                            f"{'Yes' if values['-MED1-'] else 'No'},"
                            f"{'Yes' if values['-MED2-'] else 'No'},"
                            f"{'Yes' if values['-MED3-'] else 'No'},"
                            f"{'Yes' if values['-MED4-'] else 'No'},"
                            f"{'Yes' if values['-MED5-'] else 'No'},"
                            f"{'Yes' if values['-MED6-'] else 'No'}\n")

                        # Replace selected row with edited data
                        lines[selected_row_index] = new_line

                        with open(filename, 'w') as file:
                            file.writelines(lines)

                        # Check for blood pressure alerts
                        alert = check_bp_alerts(systolic_avg, diastolic_avg)
                        if alert == "high":
                            sg.popup("⚠️ High Blood Pressure Detected in updated record!", text_color="red")
                        elif alert == "low":
                            sg.popup("⚠️ Low Blood Pressure Detected in updated record!", text_color="orange")

                        # Refresh table
                        # Reload the full data from file
                        with open(filename, 'r') as f:
                            full_row_data.clear()
                            lines = f.readlines()
                            rows = []
                            for line in lines:
                                parts = [p.strip() for p in line.strip().split(',')]
                                if len(parts) < 19:
                                    continue
                                full_row_data.append(parts)
                                rows.append([
                                    parts[0], parts[10], parts[11], parts[12],
                                    parts[13], parts[14], parts[15],
                                    parts[16], parts[17], parts[18]
                                ])
                            window['TABLE'].update(values=rows)

                        # Clear edit status
                        window['-EDIT-STATUS-'].update("✅ Record updated successfully!")

                        # Select the updated row in the table
                        if 0 <= selected_row_index < len(rows):
                            window['TABLE'].update(select_rows=[selected_row_index])
                    except FileNotFoundError:
                        sg.popup_error("Blood_Pressure_final.txt file not found. Please ensure the file exists.")
                    except IndexError:
                        sg.popup_error("Error accessing data at the selected index. The data structure may have changed.")
                    except Exception as e:
                        sg.popup_error(f"Error updating: {str(e)}")
                else:
                    sg.popup_error("Please select a row first to update.")

            case '-SAVE-':
                try:
                    s1 = int(values['s_21'])
                    s2 = int(values['s_22'])
                    s3 = int(values['s_23'])
                    d1 = int(values['d_31'])
                    d2 = int(values['d_32'])
                    d3 = int(values['d_33'])
                    p1 = int(values['p_41'])
                    p2 = int(values['p_42'])
                    p3 = int(values['p_43'])
                    _, _, _, now = get_current_datetime_info()
                    systolic_avg = round((s1 + s2 + s3) / 3)
                    diastolic_avg = round((d1 + d2 + d3) / 3)
                    pulse_avg = round((p1 + p2 + p3) / 3)

                    alert = check_bp_alerts(systolic_avg, diastolic_avg)

                    if alert == "high":
                        sg.popup("⚠️ High Blood Pressure Detected!", text_color="red")
                        window['systolic'].update(f"{systolic_avg}", text_color="red")
                        window['diastolic'].update(f"{diastolic_avg}", text_color="red")
                    elif alert == "low":
                        sg.popup("⚠️ Low Blood Pressure Detected!", text_color="orange")
                        window['systolic'].update(f"{systolic_avg}", text_color="orange")
                        window['diastolic'].update(f"{diastolic_avg}", text_color="orange")
                    else:
                        window['systolic'].update(f"{systolic_avg}", text_color="black")
                        window['diastolic'].update(f"{diastolic_avg}", text_color="black")

                    window['systolic'].update(f"{systolic_avg}")
                    window['diastolic'].update(f"{diastolic_avg}")
                    window['pulse'].update(f"{pulse_avg}")

                    with open('Blood_Pressure_final.txt', 'a') as file:
                        file.write(f"{now},"
                                   f"{s1},{s2},{s3},"
                                   f"{d1},{d2},{d3},"
                                   f"{p1},{p2},{p3},"
                                   f"{systolic_avg},{diastolic_avg},{pulse_avg},"
                                   f"{'Yes' if values['-MED1-'] else 'No'},"
                                   f"{'Yes' if values['-MED2-'] else 'No'},"
                                   f"{'Yes' if values['-MED3-'] else 'No'},"
                                   f"{'Yes' if values['-MED4-'] else 'No'},"
                                   f"{'Yes' if values['-MED5-'] else 'No'},"
                                   f"{'Yes' if values['-MED6-'] else 'No'}\n")
                    sg.popup("✅ Record saved successfully!", title="Saved")
                    # Optionally clear input fields after saving:
                    for key in ['s_21', 's_22', 's_23', 'd_31', 'd_32', 'd_33', 'p_41', 'p_42', 'p_43']:
                        window[key].update("")
                    for med_key in ['-MED1-', '-MED2-', '-MED3-', '-MED4-', '-MED5-', '-MED6-']:
                        window[med_key].update(False)

                    window['systolic'].update("")
                    window['diastolic'].update("")
                    window['pulse'].update("")

                except ValueError:
                    sg.popup_error("❗ Please ensure all blood pressure and pulse fields are numbers.")
                except Exception as e:
                    sg.popup_error(f"An error occurred while saving: {str(e)}")

                    # Refresh the table after saving
                    # Reload the full data from file
                    with open(filename, 'r') as f:
                        full_row_data.clear()
                        lines = f.readlines()
                        rows = []
                        for line in lines:
                            parts = [p.strip() for p in line.strip().split(',')]
                            if len(parts) < 19:
                                continue
                            full_row_data.append(parts)
                            rows.append([
                                parts[0], parts[10], parts[11], parts[12],
                                parts[13], parts[14], parts[15],
                                parts[16], parts[17], parts[18]
                            ])
                        window['TABLE'].update(values=rows)

                    # Clear input fields after saving
                    window['s_21'].update('')
                    window['s_22'].update('')
                    window['s_23'].update('')
                    window['d_31'].update('')
                    window['d_32'].update('')
                    window['d_33'].update('')
                    window['p_41'].update('')
                    window['p_42'].update('')
                    window['p_43'].update('')

                except ValueError:
                    sg.popup_error("Please enter valid numeric values for all readings.")
            case 'Save':  # or whatever button triggers saving
                print("[DEBUG] Keys in values:", list(values.keys()))
                print(f"[DEBUG] Raw date input: '{values.get('date')}'")
                print(f"[DEBUG] Raw time input: '{values.get('hm')}'")

                date_str = values.get('date', '').strip()
                time_str = values.get('hm', '').strip()

                if not date_str or not time_str:
                    sg.popup_error("Date and Time are required.")
                    continue
            # case 'Save':
            #     try:
            #         date_str = values['date'].strip()
            #         time_str = values['hm'].strip()
            #
            #         # ✅ Check if date or time is missing
            #         if not date_str or not time_str:
            #             sg.popup_error("Date and Time are required.")
            #             break  # Exit the SAVE case early
            #
            #         # Validate and format datetime
            #         timestamp = f"{date_str} {time_str}"
            #         dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M")  # This will now only run if both inputs exist
            #         full_timestamp = dt.strftime("%b %d %Y %H:%M:%S %A")
            #
            #         # Continue with the rest of your data collection and saving...
            #         s_values = [values['s_21'], values['s_22'], values['s_23']]
            #         d_values = [values['d_31'], values['d_32'], values['d_33']]
            #         p_values = [values['p_41'], values['p_42'], values['p_43']]
            #
            #         # Calculate averages
            #         s_avg = round(sum(map(int, s_values)) / 3)
            #         d_avg = round(sum(map(int, d_values)) / 3)
            #         p_avg = round(sum(map(int, p_values)) / 3)
            #
            #         meds = ['Yes' if values.get(f'-MED{i}-') else 'No' for i in range(1, 7)]
            #
            #         row = [full_timestamp] + s_values + d_values + p_values + [str(s_avg), str(d_avg),
            #                                                                    str(p_avg)] + meds
            #
            #         if 'editing_index' in locals() and editing_index is not None:
            #             full_row_data[editing_index] = row
            #             editing_index = None
            #             window['-EDIT-STATUS-'].update("Changes saved.")
            #         else:
            #             full_row_data.append(row)
            #             window['-EDIT-STATUS-'].update("New record added.")
            #
            #         window['TABLE'].update(values=full_row_data)
            #
            #     except ValueError:
            #         sg.popup_error("Please enter valid date and time in correct format (YYYY-MM-DD and HH:MM).")
            #     except Exception as e:
            #         sg.popup_error(f"Error saving data: {str(e)}")

            case 'TABLE':
                try:
                    selected_row_index = values['TABLE'][0] if values['TABLE'] else None
                    if selected_row_index is not None and 0 <= selected_row_index < len(full_row_data):
                        parts = full_row_data[selected_row_index]

                        # Enable the edit button when a row is selected
                        window['-EDIT-'].update(disabled=False)
                        window['-EDIT-STATUS-'].update("Row selected. Click 'Edit Selected Row' to begin editing.")
                    else:
                        # Disable the edit button when no row is selected or invalid row
                        window['-EDIT-'].update(disabled=True)
                        window['-EDIT-STATUS-'].update("")
                except Exception as e:
                    sg.popup_error(f"Error selecting row: {str(e)}")
                    window['-EDIT-'].update(disabled=True)
                    window['-EDIT-STATUS-'].update("")

            case '-excel-':
                export_to_excel()

            case 'Convert to CSV' | '-csv-':
                convert_txt_to_csv()

            case 'Weekly Line Chart' | '-WEEKLY-LINE-':

                show_chart_with_date_picker(chart_type='line', period='weekly')

            case 'Weekly Bar Chart' | '-WEEKLY-BAR-':
                show_chart_with_date_picker(chart_type='bar', period='weekly')

            case 'Monthly Line Chart' | '-MONTHLY-LINE-':
                show_chart_with_date_picker(chart_type='line', period='monthly')

            case 'Monthly Bar Chart' | '-MONTHLY-BAR-':
                show_chart_with_date_picker(chart_type='bar', period='monthly')


            case '-EXPORT-':
                export_to_excel()


            case 'Change Theme':
                new_theme = show_theme_selector()
                if new_theme:
                    window.close()
                    settings['theme'] = new_theme
                    window = create_window()

            case 'Set Save Folder':
                new_folder = choose_save_folder(current_path=settings['save_folder'])
                if new_folder:
                    settings['save_folder'] = new_folder  # store in variable or config
                    sg.popup(f"Save folder set to:\n{settings['save_folder']}")

            case 'Set Unit':
                selected_unit = choose_unit(current_unit=settings['unit'])
                if selected_unit != settings['unit']:
                    settings['unit'] = selected_unit
                    sg.popup(f"Unit set to: {settings['unit']}")

            case 'Set Date Format':
                new_fmt = choose_date_format(current_format=settings['date_format'])
                if new_fmt != settings['date_format']:
                    settings['date_format'] = new_fmt
                    sg.popup(f"Date format set to: {settings['date_format']}")

            case 'Show Summary':
                # Check if there's data to summarize
                if not full_row_data:
                    sg.popup_error("No data available. Please load data first.")
                    continue

                try:
                    # Convert the data to a pandas DataFrame
                    df = pd.DataFrame(
                        [[row[0], int(row[10]), int(row[11]), int(row[12])] for row in full_row_data if len(row) >= 13],
                        columns=['Date', 'Systolic', 'Diastolic', 'Pulse']
                    )
                    show_summary(df)
                except ValueError as e:
                    sg.popup_error(f"Error processing data values: {str(e)}", title="Data Error")
                except KeyError as e:
                    sg.popup_error(f"Missing data column: {str(e)}", title="Data Structure Error")
                except Exception as e:
                    sg.popup_error(f"Error generating summary: {str(e)}", title="Processing Error")

            case 'Detect Anomalies':
                # Check if there's data to analyze
                if not full_row_data:
                    sg.popup_error("No data available. Please load data first.")
                    continue

                try:
                    # Convert the data to a pandas DataFrame
                    df = pd.DataFrame(
                        [[row[0], int(row[10]), int(row[11]), int(row[12])] for row in full_row_data if len(row) >= 13],
                        columns=['Date', 'Systolic', 'Diastolic', 'Pulse']
                    )
                    detect_anomalies(df)
                except ValueError as e:
                    sg.popup_error(f"Error processing data values: {str(e)}", title="Data Error")
                except KeyError as e:
                    sg.popup_error(f"Missing data column: {str(e)}", title="Data Structure Error")
                except Exception as e:
                    sg.popup_error(f"Error detecting anomalies: {str(e)}", title="Processing Error")

            case 'Add/Edit Medicines':
                manage_medicines(medicine_list)

            case 'Blood Pressure Category':
                load_csv(latest_csv)

            case 'BMI Calculator':
                bmi_calculation()

            case 'Medicine Dashboard':
                medicine_dashboard_tracker(latest_csv)

            case 'Weather':
                show_weather_window()
            case '-BP-REMINDER-':
                sg.popup('⏰ Time to log your BP!', title='BP Reminder')

            case '-MED-REMINDER-':
                sg.popup('💊 Time to take your medicine!', title='Medicine Reminder')

            case 'About':
                about()

            case '-EXIT-':
                sg.popup_yes_no('Are you sure? Want to exit!')
                break

    save_settings(settings) # Save on exit
    window.close()

if __name__=="__main__":
    main()