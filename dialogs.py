import FreeSimpleGUI as sg

def show_theme_selector():
    theme_list = sg.theme_list()
    layout = [
        [sg.Text("Choose a Theme:")],
        [sg.Combo(theme_list, default_value=sg.theme(), key='-THEME-', size=(30, 20))],
        [sg.Button("Apply"), sg.Button("Cancel")]
    ]
    window = sg.Window("Select Theme", layout, modal=True)
    event, values = window.read()
    window.close()
    return values['-THEME-'] if event == "Apply" and values['-THEME-'] else None

def choose_unit(current_unit='mmHg'):
    layout = [
        [sg.Text("Select Pressure Unit:")],
        [sg.Combo(['mmHg', 'kPa'], default_value=current_unit, key='-UNIT-', size=(10,1))],
        [sg.Button("Apply"), sg.Button("Cancel")]
    ]
    window = sg.Window("Choose Unit", layout, modal=True)
    event, values = window.read()
    window.close()
    return values['-UNIT-'] if event == 'Apply' and values['-UNIT-'] else current_unit

def choose_date_format(current_format='%Y-%m-%d'):
    formats = {
        'YYYY-MM-DD': '%Y-%m-%d',
        'DD/MM/YYYY': '%d/%m/%Y',
        'MM-DD-YYYY': '%m-%d-%Y'
    }

    layout = [
        [sg.Text("Choose Date Format:")],
        [sg.Combo(list(formats.keys()), key='-DFMT-')],
        [sg.Button("Apply"), sg.Button("Cancel")]
    ]
    window = sg.Window("Date Format", layout, modal=True)
    event, values = window.read()
    window.close()

    if event == 'Apply' and values['-DFMT-']:
        return formats[values['-DFMT-']]
    return current_format

def choose_save_folder(current_path='./code/python/python_repository_files/'):
    layout = [
        [sg.Text("Choose Folder to Save Data:")],
        [sg.Input(current_path, key='-FOLDER-'), sg.FolderBrowse()],
        [sg.Button("Apply"), sg.Button("Cancel")]
    ]
    window = sg.Window("Select Save Folder", layout, modal=True)
    event, values = window.read()
    window.close()
    return values['-FOLDER-'] if event == 'Apply' and values['-FOLDER-'] else None
