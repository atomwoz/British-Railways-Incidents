import requests
import pytz
import time
import xml.etree.ElementTree as elementTree
import os
import threading
from datetime import datetime
from io import StringIO
from html.parser import HTMLParser

operators = []


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


def center_text(stri, size):
    if len(stri) >= size:
        return stri
    left = int((size - len(stri)) / 2)
    right = int(size - len(stri) - left)
    return left * "=" + stri + right * "="


def print_clock():
    while True:
        london_time = datetime.now(pytz.timezone('Europe/London'))
        print("================", london_time.strftime("%H:%M:%S"), "================", end="\r")
        time.sleep(0.2)


def main():

    i = 0
    clock = threading.Thread(target=print_clock)
    url = 'https://internal.nationalrail.co.uk/xml/5.0/incidents.xml'
    r = requests.get(url)
    incidents = elementTree.fromstring(r.content)
    for x in incidents.iter("{http://nationalrail.co.uk/xml/incident}PtIncident"):
        op_name = x.find("{http://nationalrail.co.uk/xml/incident}Affects").find(
            "{http://nationalrail.co.uk/xml/incident}Operators") \
            .find("{http://nationalrail.co.uk/xml/incident}AffectedOperator"). \
            find("{http://nationalrail.co.uk/xml/incident}OperatorName")
        if op_name.text not in operators:
            operators.append(op_name.text)

    # Choose affected carrier
    while True:
        clear_console()
        i = 0
        for x in operators:
            i += 1
            print(i, ") ", x, sep="")
        i += 1
        print(i, ") Every line", sep="")
        print("================================================================")
        print("Enter the carrier number to see the disruptions that affect it: ", end="")
        x = int(input())
        if 0 < x <= i:
            if x is i:
                op_name = ""
            else:
                op_name = operators[x - 1]
            break

    # Start clock
    clock.start()

    while True:
        # Pull XML from server
        r = requests.get(url)
        incidents = elementTree.fromstring(r.content)

        # Clear screen and print console header
        clear_console()
        print("     BRITISH RAILWAYS INCIDENTS APP")
        print("============ Affected lines ==============")
        print()
        # Iterate every accident
        for x in incidents.iter("{http://nationalrail.co.uk/xml/incident}PtIncident"):
            priority = int(x.find("{http://nationalrail.co.uk/xml/incident}IncidentPriority").text)
            cleared = x.find("{http://nationalrail.co.uk/xml/incident}ClearedIncident")
            operator = x.find("{http://nationalrail.co.uk/xml/incident}Affects").find(
                "{http://nationalrail.co.uk/xml/incident}Operators") \
                .find("{http://nationalrail.co.uk/xml/incident}AffectedOperator"). \
                find("{http://nationalrail.co.uk/xml/incident}OperatorName").text

            if cleared is not None:
                cleared = cleared.text
            else:
                cleared = "false"

            # Print info only when priority is high and accident isn't cleared
            if cleared == "false" and priority < 3 and (operator == op_name or op_name == ""):
                routes = x.find("{http://nationalrail.co.uk/xml/incident}Affects").find(
                    "{http://nationalrail.co.uk/xml/incident}RoutesAffected")
                summary = x.find("{http://nationalrail.co.uk/xml/incident}Summary")
                description = x.find("{http://nationalrail.co.uk/xml/incident}Description")
                if description is not None and summary is not None:
                    print(center_text(strip_tags(summary.text), 100))
                    print("\tDESCRIPTION: ", strip_tags(description.text))
                    print()
                    print()

        # Sleep 10s
        time.sleep(10)

        # Increase counter
        i += 1


if __name__ == "__main__":
    main()
