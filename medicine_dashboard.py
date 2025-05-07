import pandas as pd
import matplotlib.pyplot as plt
import FreeSimpleGUI as sg
import glob
import os

def medicine_dashboard_tracker(filename):

    # 🔽 Make sure to load your CSV file here
    df = pd.read_csv(filename)  # <- change to your actual CSV file path
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    # List of medicine columns (adjust as needed)
    medicine_cols = ['Multi_Vitamin', 'Telmisartan', 'Amlodipine', 'Rosuvastatin', 'B_Complex', 'Losartan']

    # Create a copy with only date and medicine status
    med_data = df[['Date'] + medicine_cols].copy()
    med_data['Date'] = pd.to_datetime(med_data['Date']).dt.strftime('%Y-%m-%d')

    med_data_display = med_data.copy()
    med_data_display[medicine_cols] = med_data_display[medicine_cols].replace({'Yes': '✅', 'No': '❌'})

    table_headings = ['Date'] + medicine_cols
    table_values = med_data_display.values.tolist()

    layout = [
        [sg.Table(values=table_values,
                  headings=table_headings,
                  auto_size_columns=True,
                  justification='center',
                  key='-TABLE-',
                  selected_row_colors="yellow on green",
                  vertical_scroll_only=False,
                  num_rows=min(15, len(table_values)))],
        [sg.Button("Close")]
    ]


    window = sg.Window('Medicine Dashboard', layout, size=(870, 380), finalize=True, resizable=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Close':
            break

        elif event == "Medicine Summary":
            pass


    window.close()

if __name__=='__main__':
    medicine_dashboard_tracker()
