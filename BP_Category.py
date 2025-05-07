import FreeSimpleGUI as sg
import pandas as pd

def classify_bp(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return 'Normal'
    elif 120 <= systolic < 130 and diastolic < 80:
        return 'Elevated'
    elif 130 <= systolic < 140 or 80 <= diastolic < 90:
        return 'Hypertension Stage 1'
    elif 140 <= systolic or 90 <= diastolic:
        return 'Hypertension Stage 2'
    elif systolic > 180 or diastolic > 120:
        return 'Hypertensive Crisis'
    else:
        return 'Unclassified'

# Load CSV
def load_csv(filename="Blood_Pressure_Data_20250506_134255.csv"):
    df = pd.read_csv(filename)

    # Add BP category column based on average values
    df['BP_Category'] = df.apply(
        lambda row: classify_bp(row['Systolic_Avg'], row['Diastolic_Avg']), axis=1
    )

    # Save new CSV (optional)
    df.to_csv("bp_data_with_category.csv", index=False)

    # Print result
    # print(df[['Date', 'Systolic_Avg', 'Diastolic_Avg', 'BP_Category']])

    data = df[['Date', 'Systolic_Avg', 'Diastolic_Avg', 'Pulse_Avg', 'BP_Category']].values.tolist()

    layout = [
        [sg.Table(values=data,
                  headings=['Date', 'Sys Avg', 'Dia Avg', 'Pulse Avg', 'Category'],
                  key='-TABLE-',
                  auto_size_columns=True,
                  justification='center',
                  enable_events=True,
                  vertical_scroll_only=False
                  )],

        [sg.B('Close')]
    ]

    window = sg.Window('Blood Pressure with Categories', layout, size=(800, 300), font=('Arial', 13))

    while True:

        event, values = window.read()
        if event in (None, 'Exit'):
            break

        match event:
            case 'Close':
                break

    window.close()