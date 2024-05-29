#!/usr/bin/python3

# pip install ping3 schedule macos_notifications
from ping3 import ping # pip install ping3
from datetime import datetime, timedelta
from schedule import every, repeat, run_pending # pip install schedule
from time import sleep
from collections import defaultdict

from mac_notifications.client import create_notification, Notification as N # pip install macos_notifications


def filter_repeats(f):
    last_args = None
    last_kwargs = None
    last_result = None
    
    def wrapper(*args, **kwargs):
        nonlocal last_args, last_kwargs, last_result
        # If arguments are the same as the previous invocation, return the cached result
        if (args, kwargs) == (last_args, last_kwargs):
            return last_result
        # Otherwise, call the function and update the cache
        last_args, last_kwargs = args, kwargs
        last_result = f(*args, **kwargs)
        return last_result
    
    return wrapper

mac_notification: N = None
def set_mac_notification(message):
    global mac_notification
    if mac_notification:
        mac_notification.cancel()
        mac_notification = None
    if message:
        mac_notification = create_notification(title="Network status", text=message)

class StateDurationTracker:
    def __init__(self):
        self.monitoring_start = None
        self.current_state = None
        self.last_change = datetime.now()
        self.states = defaultdict(timedelta)
    def change(self, state):
        current_state = self.current_state
        now = datetime.now()
        elapsed = now - self.last_change
        self.last_change = now
        if current_state:
            self.states[current_state] += elapsed
        else:
            self.monitoring_start = now 
        self.current_state = state
        return elapsed
    def ratio(self, state):
        return self.states[state] / (datetime.now() - self.monitoring_start)

state_time = {}
states = StateDurationTracker()
@filter_repeats
def log(message):
    set_mac_notification(message)
    if not message:
        message = "Nominal"
    # Format the date and time in ISO 8601 format with a space between the date and time
    formatted_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
    elapsed = states.change(message)
    elapsed = timedelta(seconds=round(elapsed.total_seconds()))
    print("{}\t{} \t{:0.2f}\t{}".format(formatted_datetime, elapsed, states.ratio(message), message))

def check_host(host):
    try:
        result = ping(host)
        if not result:
            sleep(0.01)
            result = ping(host)
    except OSError as e:
        return f"{host}: {e.strerror}"
    if not result:
        return "No connection to " + host
    return None

@repeat(every(5).seconds)
def check_status():
    result = None
    if not result:
        result = check_host('192.168.1.1')
    if not result:
        result = check_host('100.94.48.1')
    if not result:
        result = check_host('ub-build01-itest.itest-ci.lwd.int.spirent.io')
    log(result)

if __name__ == "__main__":
    try:
        print("{:19s}\t{:07}\t{}\t{}".format('Time', 'Duration', 'Ratio', 'State'))
        check_status()
        while True:
            run_pending()
            sleep(1)
    finally:
        if mac_notification:
            mac_notification.cancel()
