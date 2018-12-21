import logging
from threading import Thread
from time import sleep, time
from typing import List

from requests.exceptions import ConnectionError as RequestsConnectionError

from brainframe.client.api import codecs


class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """

    def __init__(self, api, ms_status_updates):
        """
        :param api: An API() object for interacting with the BrainFrame REST
        api.
        :param ms_status_updates: Milliseconds between calling for a zone status
        update
        """
        super().__init__(name="StatusPollerThread")
        self._api = api
        self._seconds_between_updates = ms_status_updates / 1000

        # Get something before starting the thread
        self._latest = self._api.get_latest_zone_statuses()
        self._running = True
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
            except RequestsConnectionError:
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
