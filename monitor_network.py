#!/usr/bin/python3

# pip install ping3 schedule macos_notifications
from ping3 import ping # pip install ping3
from datetime import datetime, timedelta
from time import sleep
from mac_notifications.client import create_notification, Notification as N # pip install macos_notifications

from state_monitor import StateDurationTracker, filter_repeats 

mac_notification: N = None
def set_mac_notification(message):
    global mac_notification
    if mac_notification:
        mac_notification.cancel()
        mac_notification = None
    if message:
        mac_notification = create_notification(title="Network status", text=message)

state_time = {}
states = StateDurationTracker()
@filter_repeats
def log(message):
    set_mac_notification(message)
    if not message:
        message = "Nominal"
    # Format the date and time in ISO 8601 format with a space between the date and time
    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
    elapsed_tuple = states.change(message)
    if elapsed_tuple:
        elapsed = timedelta(seconds=round(elapsed_tuple[1].total_seconds()))
        print("{}\t{} \t{:0.2f}\t{}".format(formatted_datetime, elapsed, states.ratio(message), message))

def check_host(host):
    try:
        result = ping(host)
        if not result:
            sleep(1)
            result = ping(host)
    except OSError as e:
        return f"{host}: {e.strerror}"
    if not result:
        return "No connection to " + host
    return None

def check_status():
    result = None
    if not result:
        result = check_host('192.168.1.1')
    if not result:
        result = check_host('100.94.48.1')
    if not result:
        result = check_host('ya.ru')
    if not result:
        result = check_host('ub-build01-itest.itest-ci.lwd.int.spirent.io')
    log(result)

if __name__ == "__main__":
    try:
        print("{:19}\t{:7}\t{}\t{}".format('Time', 'Duration', 'Ratio', 'State'))
        while True:
            check_status()
            sleep(5)
    finally:
        if mac_notification:
            mac_notification.cancel()
