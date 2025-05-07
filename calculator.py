import FreeSimpleGUI as sg
import os

HISTORY_FILE = 'calc_history.txt'
history = []
# Load history from file if exists
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, 'r') as f:
        history = f.read().splitlines()
else:
    history = []

sg.theme('DarkBlue3')

def calculate():
    # Initialize history


    calculate = [
        [sg.B('7', size=(4, 2), font=('Helvetica', 20)),sg.B('8',  size=(4, 2), font=('Helvetica', 20)),
         sg.B('9',  size=(4, 2), font=('Helvetica', 20)), sg.B('/', size=(4, 2), font=('Helvetica', 20))],


    [sg.B('4', size=(4, 2), font=('Helvetica', 20)),sg.B('5',  size=(4, 2), font=('Helvetica', 20)),
     sg.B('6',  size=(4, 2), font=('Helvetica', 20)), sg.B('*', size=(4, 2), font=('Helvetica', 20))],


    [sg.B('1', size=(4, 2), font=('Helvetica', 20)),sg.B('2',  size=(4, 2), font=('Helvetica', 20)),
     sg.B('3',  size=(4, 2), font=('Helvetica', 20)), sg.B('-', size=(4, 2), font=('Helvetica', 20))],

    [sg.B('0', size=(4, 2), font=('Helvetica', 20)),sg.B('.',  size=(4, 2), font=('Helvetica', 20)),
         sg.B('=',  size=(4, 2), font=('Helvetica', 20)), sg.B('+', size=(4, 2), font=('Helvetica', 20))]]

    calc = sg.Frame('Calculate', calculate)

    hist_readings = sg.Frame('Calculation History', [
    [sg.T('Result: ', font=('Helvetica', 16))],
    [sg.Multiline('\n'.join(history[-5:]), size=(28, 5), key='-HISTORY-', disabled=True, autoscroll=True,
                  font=('Helvetica', 16))],
    [sg.B('Clear History', size=(10, 2), font=('Helvetica', 16)),
     sg.B('Copy Last Entry', size=(10, 2), font=('Helvetica', 16))]]
                             )


    # Initialize history list
    layout = [
        [sg.Input(default_text='0', key='-DISPLAY-', focus=True, font=('Roboto Mono', 30), size=(40, 1), justification='right')],
        [sg.Col([[calc]]), sg.VerticalSeparator(), sg.Col([[hist_readings]])],
        [sg.B('Clear', size=(4, 2), font=('Helvetica', 16), pad=((10,10), (10, 10))), sg.B('Exit', size=(4, 2), font=('Helvetica', 16) ,pad=((10,10), (10, 10)))],

    ]

    window = sg.Window('Smart Calculator', layout, size=(700, 560), return_keyboard_events=True, use_default_focus=False, resizable=True, finalize=True)
    current = ""

    def update_display():
        window['-DISPLAY-'].update(current)

    def update_history():
        window['-HISTORY-'].update('\n'.join(history[-5:]))
        with open(HISTORY_FILE, 'w') as f:
            f.write('\n'.join(history))

    while True:
        event, values = window.read()
        # print(event)
        # print(values)
        if event in (sg.WIN_CLOSED, 'Exit'):
            break

        # Sync manual input from the Input field
        elif event == '-DISPLAY-':
            current = values['-DISPLAY-']  # Don't append; replace current
            continue  # Skip further processing

        elif event == 'Clear':
            current = ""
            update_display()


        elif event in ('=', '\r', 'Return'):
            try:
                result = str(eval(current))
                entry = f"{current} = {result}"
                history.append(entry)
                update_display()

                window['-DISPLAY-'].update(value=result)
                current = str(result)
                update_history()

            except:
                window['-DISPLAY-'].update(value="Error")
                current = ""

        elif event == 'Clear History':
            history.clear()
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            window['-HISTORY-'].update('')

        elif event == 'Copy Last Entry':
            if history:
                sg.clipboard_set(history[-1])
                sg.popup('Last entry copied to clipboard.', title='Copied')

        elif 'BackSpace' in event:
            current = current[:-1]
            update_display()

        elif len(event) == 1 and event in '0123456789+-*/().':
            current += event
            update_display()

        # # Sync typed values if someone types into the input box manually
        # if event == '-DISPLAY-':
        #     current = values['-DISPLAY-']
        #     continue  # Don't process this further

        else:
            current += event
            window['-DISPLAY-'].update(value=current)


    window.close()