from time import sleep
import ephem
from datetime import date, datetime, timedelta
# import utilities.config as config
from config import config


class TimeHelper:
    site_location = ephem.Observer()

    def __init__(self):
        self.site_location.lat = config["latitude"]
        self.site_location.lon = config["longitude"]
        self.site_location.utcdate = datetime.utcnow()
        self.site_location.date = datetime.now()
        self.site_location.elevation = config["elevation"]
        self.site_location.horizon = config["horizon"]
        self.sun = ephem.Sun()
        self.offset = 43.0

    def getSunrise(self):
        return ephem.localtime(self.site_location.next_rising(self.sun))

    def getSunriseUtcCorrect(self):
        valEphem = self.site_location.next_rising(self.sun)
        valEphemD = valEphem.datetime() + timedelta(minutes = self.offset)
        return valEphemD

    def getSunset(self):
        return ephem.localtime(self.site_location.next_setting(self.sun))

    def getSunsetUtcCorrect(self):
        valEphem = self.site_location.next_setting(self.sun)
        valEphemD = valEphem.datetime() + timedelta(minutes = self.offset)
        return valEphemD

    def getHousekeeping(self):
        return self.getSunset() - timedelta(minutes=config["startHousekeeping"])

    def waitUntilHousekeeping(self, deltaMinutes=0):
        while (datetime.now() < self.getHousekeeping() + timedelta(minutes=deltaMinutes)):
            sleep(5)
        return

    def waitUntilStartTime(self):
        while (datetime.now() < self.getSunset()):
            sleep(5)
        return
    
    
