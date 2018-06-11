import logging
from typing import List, Tuple, Union, Optional
from threading import Thread
from time import sleep, time

from brainframe.client.api import codecs



class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """

    def __init__(self, api, ms_status_updates):
        """
        :param api: An API() object for interacting with the BrainFrame REST
        api.
        :param ms_status_updates: Miliseconds between calling for a zone status
        update
        """
        super().__init__(name="StatusPollerThread")
        self._api = api
        self._seconds_between_updates = ms_status_updates / 1000
        self._running = False

        # Get something before starting the thread
        self._latest = self._api.get_latest_zone_statuses()
        self.start()

    def run(self):
        """Polls Brainserver for ZoneStatuses at a constant rate"""
        self._running = True
        call_time = 0
        while self._running:

            # Call the server, timing how long the call takes
            try:
                start = time()
                latest = self._api.get_latest_zone_statuses()
                self._latest = latest
                call_time = time() - start
            except ConnectionError:
                logging.warning("StatusLogger: Could not reach server!")
                sleep(2)

            # Sleep for the appropriate amount to keep call times consistent
            time_left = self._seconds_between_updates - call_time
            if time_left > 0:
                sleep(time_left)

        self._running = False

    @property
    def is_running(self):
        return self._running

    # def get_alarm(self, stream_id, alarm_id) -> Optional[codecs.ZoneAlarm]:
    #     """Return a list of unverified alerts for this stream_id"""
    #     zones = self.get_zones(stream_id)
    #     if len(zones) == 0:
    #         return None
    #     alarms = sum([zone.alarms for zone in zones], [])
    #     alarms = [alarm for alarm in alarms if alarm.id == alarm_id]
    #     if len(alarms) == 0:
    #         return None
    #     return alarms[0]
    #
    # def get_zone(self, stream_id, zone_id) -> Optional[codecs.Zone]:
    #     for zone in self.get_zones(stream_id):
    #         if zone.id == zone_id:
    #             return zone
    #     return None

    # def get_zones(self, stream_id) -> List[codecs.Zone]:
    #     statuses = self.latest_statuses(stream_id)
    #     zones = [status.zone for status in statuses]
    #     return zones

    def latest_statuses(self, stream_id) -> List[codecs.ZoneStatus]:
        """Returns the latest cached list of ZoneStatuses for that stream_id"""
        latest = self._latest
        if stream_id not in latest:
            return []
        return latest[stream_id]

    def close(self):
        """Close the status polling thread"""
        self._running = False
        self.join()