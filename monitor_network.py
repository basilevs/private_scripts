from ping3 import ping
from datetime import datetime
from schedule import every, repeat, run_pending
from time import sleep

from mac_notifications.client import create_notification, Notification as N


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

@filter_repeats
def log(message):
    now = datetime.now()
    set_mac_notification(message)
    if not message:
        message = "Nominal"

    # Format the date and time in ISO 8601 format with a space between the date and time
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S:")
    print(formatted_datetime, message)

def check_host(host):
    try:
        result = ping(host)
    except OSError as e:
        return f"{host}: {e.strerror}"
    if not result:
        return "No connection to " + host
    return None

@repeat(every(5).seconds)
def check_status():
    result = check_host('192.168.1.1')
    if not result:
        result = check_host('100.94.48.1')
    log(result)

if __name__ == "__main__":
    try:
        while True:
            run_pending()
            sleep(1)
    finally:
        if mac_notification:
            mac_notification.cancel()
