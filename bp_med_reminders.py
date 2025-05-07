import threading
import datetime
import time

def reminder_loop(window, bp_times, med_times, test_mode=False):
    while True:
        now = datetime.datetime.now().strftime('%H:%M')
        if test_mode:
            # In test mode, simulate reminders every 10 seconds
            window.write_event_value('-BP-REMINDER-', now)
            window.write_event_value('-MED-REMINDER-', now)
            time.sleep(10)
        else:
            if now in bp_times:
                window.write_event_value('-BP-REMINDER-', now)
            if now in med_times:
                window.write_event_value('-MED-REMINDER-', now)
            time.sleep(60)
