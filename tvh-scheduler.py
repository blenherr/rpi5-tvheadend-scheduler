"""
!/usr/bin/env python
This Python file uses the following encoding: utf-8

GPL-3.0 license
"""

# Standard librarys
import os
import time
from datetime import datetime
import requests
from requests.auth import HTTPDigestAuth
import socket
import subprocess
import logging

# Tvheadend server
HOST = "localhost"
PORT = "9981"
USER = "autopoweroff"
PASS = "password"

# Number of seconds the system must run before shutting down. This enables:
#   - Scanning the EPG and updating automatic recordings via Tvheadend.
#   - Establishing an SSH connection by a user.
MIN_UPTIME = 1200

# Minimum time gap in seconds for shutdown before the next recording.
# If the gap is shorter, the system does not switch off, but waits for the recording.
MIN_GAP_TIME = 600

# Time in seconds used for starting before the scheduled recording time.
PRE_SCHEDULE_TIME = 120

# Sleep time in seconds (Sleep this script for the specified time).
SLEEP_TIME = 60

# Logging
dir_path = os.path.dirname(os.path.realpath(__file__))
os.makedirs(dir_path + "/logs", exist_ok=True)
now = datetime.now()
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(lineno)-4d %(funcName)s(): %(message)s",
    filename=dir_path + "/logs/%s.log" % (now.strftime("%Y_%m_%d")),
    datefmt="%H:%M:%S",
    level=logging.ERROR,
)
LOGGER = logging.getLogger(__name__)
LOGGER.debug("")
LOGGER.debug("Autopoweroff python script has started")


def uptime():
    """Get uptime. Return value in seconds or False"""
    try:
        return int(subprocess.getoutput("awk '{print int($1)}' /proc/uptime"))
    except Exception as e:
        LOGGER.error(e)
        return False


def tvheadend_running():
    """Is Tvheadend running? Return True or False"""
    args = socket.getaddrinfo(HOST, PORT, socket.AF_INET, socket.SOCK_STREAM)
    for family, socktype, proto, canonname, sockaddr in args:
        s = socket.socket(family, socktype, proto)
        try:
            s.connect(sockaddr)
        except socket.error as e:
            LOGGER.error(e)
            return False
        else:
            s.close()
            return True


def get_tvheadend_activity():
    """Get Tvheadend activity from API"""
    try:
        ACTIVITY_PATH = "/api/status/activity"
        return requests.get("http://" + HOST + ":" + str(PORT) + ACTIVITY_PATH, auth=HTTPDigestAuth(USER, PASS))
    except Exception as e:
        LOGGER.error(e)
        return None


def create_json(response):
    """Create a Json object"""
    try:
        return response.json()
    except Exception as e:
        LOGGER.error(e)
        return None


def set_rtc(next_wakeup):
    """Set RTC wake alarm. Return value in seconds or False"""
    try:
        # Reset RTC wake alarm
        if int(subprocess.getoutput("echo 0 | sudo tee /sys/class/rtc/rtc0/wakealarm")) != 0:
            return False
        # Set RTC wake alarm
        return int(subprocess.getoutput("echo " + next_wakeup + " | sudo tee /sys/class/rtc/rtc0/wakealarm"))
    except ValueError as e:
        LOGGER.error(e)
        return False


def suspend_rpi():
    """Suspend Raspberry Pi 5. Return True or False"""
    try:
        subprocess.run("sudo halt", shell=True)
        return True
    except Exception as e:
        LOGGER.error(e)
        return False


def main():
    """Suspend Raspberry Pi 5 for next recording"""
    LOGGER.debug("")
    LOGGER.debug("New cycle started")

    # Is an SSH client connected?
    if len(subprocess.getoutput("who")) > 0:
        LOGGER.debug("SSH user is connected. Abort script.")
        return
    else:
        LOGGER.debug("No SSH user is connected. Proceed script.")

    # Get system uptime in seconds
    UPTIME = uptime()
    if not UPTIME:
        LOGGER.debug("System uptime is not valid. Abort script.")
        return
    else:
        LOGGER.debug("System uptime is " + str(UPTIME) + "s. Proceed script.")

    # Has the system been running long enough?
    if UPTIME <= MIN_UPTIME:
        LOGGER.debug("The system doesn not run long enough. Abort script.")
        return
    else:
        LOGGER.debug("The system runs long enough. Proceed script.")

    # Is Tvheadend is running?
    if not tvheadend_running():
        LOGGER.debug("Tvheadend is DOWN. Abort script.")
        return
    else:
        LOGGER.debug("Tvheadend is UP. Proceed script.")

    # Get Tvheadend activity
    RESPONSE = get_tvheadend_activity()
    if RESPONSE.status_code != 200 or RESPONSE == None:
        LOGGER.debug("Tvheadend response is " + str(RESPONSE.status_code) + ". Abort script.")
        return
    else:
        LOGGER.debug("Tvheadend response is " + str(RESPONSE.status_code) + ". Proceed script.")

    # Create Json object
    ACTIVITY_JSON = create_json(RESPONSE)
    if ACTIVITY_JSON == None or ACTIVITY_JSON == "":
        LOGGER.debug("Not a Json object. Abort script.")
        return
    else:
        LOGGER.debug("Json object created. Proceed script.")

    # Is a Tvheadend client (Kodi, etc.) connected?
    if ACTIVITY_JSON["connection_count"] > 0:
        LOGGER.debug(str(ACTIVITY_JSON["connection_count"]) + " client(s) connected to Tvheadend. Abort script.")
        return
    else:
        LOGGER.debug("No Client(s) connected to Tvheadend. Proceed script.")

    # Is Tvheadend next activity in the past?
    # DVR recordings in progress are also included, therefore, the reported DVR time may be in the past.
    if ACTIVITY_JSON["next_activity"] < ACTIVITY_JSON["current_time"]:
        LOGGER.debug("DVR recordings are in progress. Abort script.")
        return
    else:
        LOGGER.debug("DVR recordings not in progress. Proceed script.")

    # Is the time gap until the next activity long enough?
    GAP = ACTIVITY_JSON["next_activity"] - ACTIVITY_JSON["current_time"]
    if GAP <= MIN_GAP_TIME:
        LOGGER.debug(
            "The time gap until the next activity is " + str(GAP) + " seconds, which is too short. Abort script."
        )
        return
    else:
        LOGGER.debug(
            "The time gap until the next activity is " + str(GAP) + " seconds, which is long enough. Proceed script."
        )

    # Calculate next wakeup unix time
    NEXT_WAKE_TIME = str(ACTIVITY_JSON["next_activity"] - PRE_SCHEDULE_TIME)

    # Set RTC wake alarm
    if not set_rtc(NEXT_WAKE_TIME):
        LOGGER.debug("Setting the RTC wake alarm is not possible. Abort script.")
        return
    else:
        LOGGER.debug("Setting the RTC wake alarm is complete. Proceed script.")

    # Suspend Raspberry Pi 5
    if not suspend_rpi():
        LOGGER.debug("Suspending the Raspberry Pi is not possible. Abort script.")
        return


if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(SLEEP_TIME)
        except Exception as e:
            LOGGER.error(e)
