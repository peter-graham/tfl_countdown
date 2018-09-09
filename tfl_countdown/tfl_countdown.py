import urllib, json
from datetime import datetime
import time


class TfLArrivals:
    """Maintain a list of rail arrivals/departures using the TfL API.
       Note: All timestamps are in UTC."""
    URL = "https://api.tfl.gov.uk/StopPoint/{}/arrivals"

    def __init__(self, stop):
        self.stop_point = stop
        self.trains = dict()

    def arrivals_by_platform(self, platform=None):
        """Returns a list of departure times, in seconds"""
        result = []
        for train in self.trains.values():
            if platform is None or train["platformName"] == platform:
                result.append(train["timeToStation"])
        return sorted(result)

    def arrivals_by_destination(self):
        """Returns a dict of departure times, each value is a list of times in secs"""
        result = dict()
        for train in self.trains.values():
            dest = train["destinationName"]

            # populate destination dict
            if dest not in result:
                result[dest] = []

            # populate arrival times
            result[dest].append(train["timeToStation"])

        # sort each list of departures once populated
        for departures in result.values():
            departures.sort()

        return result

    def timestamps_by_destination(self):
        """Returns a dict of departure times, each value is a list of times as str"""
        result = dict()
        for train in self.trains.values():
            dest = train["destinationName"]

            # populate destination dict
            if dest not in result:
                result[dest] = []

            # populate arrival times
            result[dest].append(train["expectedArrival"])

        # sort each list of departures once populated
        for departures in result.values():
            departures.sort()

        return result

    def tidy(self):
        to_tidy = []
        for id, train in self.trains.iteritems():
            if self.convert_date(train["timeToLive"]) <= datetime.utcnow():
                to_tidy.append(id)

        for id in to_tidy:
            del self.trains[id]

    def refresh(self):
        response = urllib.urlopen(self.URL.format(self.stop_point))
        data = json.loads(response.read())
        for train in data:
            self.trains[train["vehicleId"]] = train

    @staticmethod
    def convert_date(date):
        return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

# Test application
destination = "Stratford (London) Rail Station"
x = TfLArrivals("910GCSEAH")

while(True):
    x.refresh()
    x.tidy()
    times = x.arrivals_by_destination()
    if destination in times:
        print("Departures {}".format(map(lambda x: x//60, times)))
    else:
        print("No departures")
    time.sleep(60)