import FreeSimpleGUI as sg
from bmi_functions import classify_bmi_category, kgs_to_pounds, lbs_to_kgs,feet_inches_to_meters,meters_to_feet_inches


def bmi_calculation():
    sg.theme('GreenTan')
    input_size = (15, 1)

    layout = [
        [sg.Push(), sg.T("Body Mass Index Calculator", font=('Arial', 20)), sg.Push()],
        [sg.T('Enter weight (either in kg or lbs): ')],
        [sg.HorizontalSeparator()],
        [sg.T('Kilograms: '), sg.I(size=input_size, key='kg', enable_events=True), sg.VerticalSeparator(), sg.T('Pounds: '), sg.I(size=input_size, key='lbs', enable_events=True)],
        [sg.HorizontalSeparator()],
        [sg.T('Enter height: (either in feet/inches  or meters): ')],
        [sg.HorizontalSeparator()],
        [sg.T('Feet/Inches: '), sg.I(size=input_size, key='ft_inch', enable_events=True), sg.VerticalSeparator(), sg.T('Meters: '),sg.I(size=input_size, key='meter', enable_events=True)],
        [sg.HorizontalSeparator()],
        [sg.Button('Submit'), sg.Button('Cancel', button_color=('white', 'green')), sg.Button("Exit", button_color=('white', 'tomato'))],

    ]

    window = sg.Window('Body Mas Index', layout, size=(650, 300), resizable=True, font=('Arial', 16))


    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        try:

            if event == 'kg' and values['kg']:
                kg = float(values['kg'])
                window['lbs'].update(f"{kgs_to_pounds(kg):.2f}")

            elif event == 'lbs' and values['lbs']:
                lbs = float(values['lbs'])
                window['kg'].update(f"{lbs_to_kgs(lbs):.2f}")

            elif event == 'ft_inch' and values['ft_inch']:
                # Expect input like "5 7"
                parts = values['ft_inch'].strip().replace(', ', '').split()
                if len(parts) > 1:
                    feet = int(parts[0])
                    inches = int(parts[1])
                    meters = feet_inches_to_meters(feet, inches)
                    window['meter'].update(f"{meters:.2f}")

            elif event == 'meter' and values['meter']:
                m = float(values['meter'])
                feet, inches = meters_to_feet_inches(m)
                window['ft_inch'].update(value=f"{feet} {inches}")

            elif event == 'Submit':
                bmi = float(values['kg']) / (float(values['meter']) * float(values['meter']))
                sg.popup(f"Your BMI is: {bmi:.2f}\n{classify_bmi_category(bmi)}", font=('Arial', 15))

        except ValueError:
            # Invalid input (non-numeric), ignore or show error
            pass


    window.close()