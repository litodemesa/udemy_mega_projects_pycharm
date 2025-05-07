import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import FreeSimpleGUI as sg
from datetime import datetime, timedelta
import numpy as np
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
import re

def load_bp_data():
    """
    Load blood pressure data from the file and return as a pandas DataFrame
    """
    try:
        data = []
        with open('Blood_Pressure_final.txt', 'r') as file:
            for line in file:
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) < 19:  # Ensure enough data in the line
                    continue
                
                # Extract date and values
                date_str = parts[0]
                systolic_avg = int(parts[10]) if parts[10].isdigit() else 0
                diastolic_avg = int(parts[11]) if parts[11].isdigit() else 0
                pulse_avg = int(parts[12]) if parts[12].isdigit() else 0
                
                # Convert date string to datetime object
                try:
                    # Try different date formats that might be in the file
                    try:
                        # Try to parse format like "Jan 10 2025 8:28:52 Friday"
                        # Extract the date part without the weekday at the end
                        date_parts = date_str.split()
                        if len(date_parts) >= 4:  # At least MMM DD YYYY HH:MM:SS format
                            # Join the first 4 parts (month, day, year, time)
                            date_time_str = ' '.join(date_parts[:4])
                            date = datetime.strptime(date_time_str, '%b %d %Y %H:%M:%S')
                        else:
                            # If format doesn't match expected pattern, try standard formats
                            raise ValueError("Date format doesn't match expected pattern")
                    except:
                        try:
                            # Try standard ISO format
                            date = datetime.strptime(date_str.split()[0], '%Y-%m-%d')
                        except:
                            try:
                                # Try with time
                                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            except:
                                # Last attempt - try to extract just the date portions
                                parts = re.findall(r'(\w+)\s+(\d+)\s+(\d{4})', date_str)
                                if parts:
                                    month, day, year = parts[0]
                                    date_str_fixed = f"{month} {day} {year}"
                                    date = datetime.strptime(date_str_fixed, '%b %d %Y')
                                else:
                                    raise ValueError(f"Could not parse date: {date_str}")
                    
                    data.append({
                        'date': date,
                        'systolic': systolic_avg,
                        'diastolic': diastolic_avg,
                        'pulse': pulse_avg
                    })
                except Exception as e:
                    print(f"Error parsing date {date_str}: {e}")
                    continue
                    
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('date')
        return df
    except Exception as e:
        sg.popup_error(f"Error loading data: {e}")
        return pd.DataFrame()

def get_date_range(period, end_date=None):
    """
    Get start and end dates based on the period (weekly or monthly)
    """
    if end_date is None:
        end_date = datetime.now()
    
    if period == 'weekly':
        start_date = end_date - timedelta(days=7)
    elif period == 'monthly':
        start_date = end_date - relativedelta(months=1)
    else:
        # Default to 1 week if invalid period
        start_date = end_date - timedelta(days=7)
        
    return start_date, end_date

def filter_data_by_date_range(df, start_date, end_date):
    """
    Filter the dataframe based on date range
    """
    if df.empty:
        return df
        
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    return df.loc[mask].copy()

def date_picker_dialog(title="Select Date Range"):
    """
    Display a dialog for selecting a date range
    """
    layout = [
        [sg.Text("Select End Date (Default: Today)")],
        [sg.Input(key='-END-DATE-', readonly=True), 
         sg.CalendarButton('Calendar', target='-END-DATE-', format='%Y-%m-%d')],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]
    
    window = sg.Window(title, layout, modal=True)
    
    result = None
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if event == 'OK':
            try:
                if values['-END-DATE-']:
                    result = datetime.strptime(values['-END-DATE-'], '%Y-%m-%d')
                else:
                    result = datetime.now()
                break
            except Exception as e:
                sg.popup_error(f"Invalid date format: {e}")
    
    window.close()
    return result

def draw_figure(canvas, figure):
    """
    Draw a matplotlib figure on a FreeSimpleGUI canvas
    """
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def create_line_chart(df, title):
    """
    Create a line chart for blood pressure data
    """
    if df.empty:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot data
    ax.plot(df['date'], df['systolic'], 'r-', label='Systolic', marker='o', linewidth=2)
    ax.plot(df['date'], df['diastolic'], 'b-', label='Diastolic', marker='s', linewidth=2)
    ax.plot(df['date'], df['pulse'], 'g-', label='Pulse', marker='^', linewidth=2)
    
    # Formatting
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Value (mmHg / BPM)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Format date on x-axis
    date_format = mdates.DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(date_format)
    if len(df) > 10:
        plt.xticks(rotation=45)
    
    # Add reference lines for normal blood pressure
    ax.axhline(y=120, color='r', linestyle='--', alpha=0.3)
    ax.axhline(y=80, color='b', linestyle='--', alpha=0.3)
    
    # Add legend
    ax.legend()
    
    plt.tight_layout()
    return fig

def create_bar_chart(df, title):
    """
    Create a grouped bar chart for blood pressure data
    """
    if df.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set up positions for grouped bars
    x = np.arange(len(df))
    width = 0.25
    
    # Plot bars
    ax.bar(x - width, df['systolic'], width, label='Systolic', color='red', alpha=0.7)
    ax.bar(x, df['diastolic'], width, label='Diastolic', color='blue', alpha=0.7)
    ax.bar(x + width, df['pulse'], width, label='Pulse', color='green', alpha=0.7)
    
    # Formatting
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Value (mmHg / BPM)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([d.strftime('%m-%d') for d in df['date']], rotation=45)
    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    
    # Add reference lines for normal blood pressure
    ax.axhline(y=120, color='r', linestyle='--', alpha=0.3)
    ax.axhline(y=80, color='b', linestyle='--', alpha=0.3)
    
    # Add legend
    ax.legend()
    
    plt.tight_layout()
    return fig

def show_chart_with_date_picker(chart_type='line', period='weekly'):
    """
    Main function to show blood pressure charts with date picker for selecting range
    
    Parameters:
    - chart_type: 'line' or 'bar'
    - period: 'weekly' or 'monthly'
    """
    # Load data
    df = load_bp_data()
    if df.empty:
        sg.popup_error("No data available or failed to load data.")
        return
    
    # Get end date from user (or use today)
    end_date = date_picker_dialog(f"Select End Date for {period.capitalize()} View")
    if end_date is None:  # User canceled
        return
    
    # Calculate date range
    start_date, end_date = get_date_range(period, end_date)
    
    # Filter data
    filtered_df = filter_data_by_date_range(df, start_date, end_date)
    
    if filtered_df.empty:
        sg.popup_error(f"No data available in the selected {period} period.")
        return
    
    # Create chart title
    period_text = "Week" if period == 'weekly' else "Month"
    title = f"Blood Pressure Data for {period_text} Ending {end_date.strftime('%Y-%m-%d')}"
    
    # Create appropriate chart
    if chart_type == 'line':
        fig = create_line_chart(filtered_df, title)
    else:  # bar chart
        fig = create_bar_chart(filtered_df, title)
    
    if fig is None:
        sg.popup_error("Failed to create chart.")
        return
    
    # Display chart in a new window
    layout = [
        [sg.Text(title, font=("Helvetica", 16))],
        [sg.Canvas(key='-CANVAS-', size=(640, 480))],
        [sg.Button('Close')]
    ]
    
    window = sg.Window(f'Blood Pressure {chart_type.capitalize()} Chart', layout, finalize=True, resizable=True)
    
    # Draw figure on canvas
    figure_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)
    
    # Event loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Close'):
            break
    
    # Cleanup
    plt.close('all')
    window.close()

def load_date_day_time(date_str):
    """
    Parse a date string and return date, time and weekday
    """
    try:
        # Try to parse the input date string
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return (dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), dt.strftime('%A'))
    except:
        # If parsing fails, return current date/time
        dt = datetime.now()
        return (dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M'), dt.strftime('%A'))

def convert_txt_to_csv():
    """
    Converts Blood_Pressure_final.txt to a CSV file with proper headers
    """
    try:
        # Define column headers for the CSV file
        headers = ['Date', 
                  'Systolic_1', 'Systolic_2', 'Systolic_3',
                  'Diastolic_1', 'Diastolic_2', 'Diastolic_3',
                  'Pulse_1', 'Pulse_2', 'Pulse_3',
                  'Systolic_Avg', 'Diastolic_Avg', 'Pulse_Avg',
                  'Multi_Vitamin', 'Telmisartan', 'Amlodipine',
                  'Rosuvastatin', 'B_Complex', 'Losartan']
        
        # Prepare data for CSV
        data_rows = []
        
        # Read the text file
        with open('Blood_Pressure_final.txt', 'r') as file:
            for line in file:
                parts = [p.strip() for p in line.strip().split(',')]
                if len(parts) < 19:  # Ensure enough data in the line
                    continue
                data_rows.append(parts)
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'Blood_Pressure_Data_{timestamp}.csv'
        
        # Write to CSV file
        with open(output_file, 'w', newline='') as csvfile:
            writer = pd.DataFrame(data_rows, columns=headers)
            writer.to_csv(csvfile, index=False)
            
        sg.popup(f"Successfully converted to CSV file: {output_file}")
        return output_file
    
    except Exception as e:
        sg.popup_error(f"Error converting to CSV: {e}")
        return None
