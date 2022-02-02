import requests
import pytz
import time
import xml.etree.ElementTree as elementTree
import os
import threading
from datetime import datetime, timezone
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def print_Clock():
    while True:
        london_time = datetime.now(pytz.timezone('Europe/London'))
        print("===============", london_time.strftime("%H:%M:%S"), "===============", end="\r")
        time.sleep(0.2)


def main():
    i = 0
    x = threading.Thread(target=print_clock)
    x.start()

    while True:
        # Pull XML from server
        url = 'https://internal.nationalrail.co.uk/xml/5.0/incidents.xml'
        r = requests.get(url)
        incidents = elementTree.fromstring(r.content)

        # Clear screen and print console header
        clear_console()
        print("     BRITISH RAILWAYS INCIDENTS APP")
        print("============Affected lines==============")
        print()

        # Iterate every accident
        for x in incidents.iter("{http://nationalrail.co.uk/xml/incident}PtIncident"):
            priority = int(x.find("{http://nationalrail.co.uk/xml/incident}IncidentPriority").text)
            cleared = x.find("{http://nationalrail.co.uk/xml/incident}ClearedIncident")
            if cleared is not None:
                cleared = cleared.text
            else:
                cleared = "false"
            # Print info only when priority is high and accident isn't cleared
            if cleared == "false" and priority < 3:
                s = x.find("{http://nationalrail.co.uk/xml/incident}Affects").find(
                    "{http://nationalrail.co.uk/xml/incident}RoutesAffected").text
                print(strip_tags(s))

        # Sleep 10s
        time.sleep(10)

        # Increase counter
        i += 1


if __name__ == "__main__":
    main()
