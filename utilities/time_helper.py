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
        self.site_location.date = datetime.now()
        self.site_location.elevation = config["elevation"]
        self.site_location.horizon = config["horizon"]
        self.sun = ephem.Sun()
        # Don't need an offset, since the goal is way past sunset and
        # way before sunrise:
        self.offset = 0.0
        self.utcdate = datetime.utcnow()

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
        valEphemD = valEphem.datetime() - timedelta(minutes = self.offset)
        return valEphemD

    def getHousekeeping(self):
        return self.getSunset() - timedelta(minutes=config["startHousekeeping"])

    def getHousekeepingUtcCorrect(self):
        return self.getSunsetUtcCorrect() - \
            timedelta(minutes=config["startHousekeeping"])

    def waitUntil(self, ut):
        wt = (ut - datetime.utcnow()).total_seconds()/60.0
        print('Wait time ... ', wt, ' minutes')
        while (wt > 0): 
            wt = (ut - datetime.utcnow()).total_seconds() / 60.0
            print('Wait time ... ', wt, ' minutes')
            sleep(5)
        return
        
    
    def waitUntilHousekeeping(self, deltaMinutes=0):
        house = self.getHousekeepingUtcCorrect() + \
            timedelta(minutes=deltaMinutes)
        self.waitUntil(house)
        return

    def waitUntilStartTime(self):
        while (datetime.now() < self.getSunset()):
            sleep(5)
        return

    def waitUntilStartTimeUtc(self):
        sunset = self.getSunsetUtcCorrect()
        self.waitUntil(sunset)
        return

    def beforeSunrise(self, exposure):
        ut = datetime.utcnow() + timedelta(seconds = exposure)
        sunrise = self.getSunriseUtcCorrect()
        if (ut < sunrise):
            print('Time until sunrise (minutes) : ', \
                  (sunrise-ut).total_seconds()/60.0)
            return True
        else:
            return False
    
