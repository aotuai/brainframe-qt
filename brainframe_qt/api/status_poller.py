import logging
import ujson
from threading import Thread
from time import sleep, time
from typing import Dict

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError

from brainframe.client.api import codecs


class StatusPoller(Thread):
    """ This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream. """

    def __init__(self, api):
        """
        :param api: An API() object for interacting with the BrainFrame REST
            api
        :param ms_status_updates: Milliseconds between calling for a zone
            status update
        """
        super().__init__(name="StatusPollerThread")
        self._api = api

        # Get something before starting the thread
        self._latest = self._api.get_latest_zone_statuses()
        self._running = True
        self.start()

    def run(self):
        """Polls BrainFrame for ZoneStatuses at a constant rate"""
        self._running = True

        zstatus_stream = self._api.get_zone_status_stream()
        while self._running:

            try:
                zone_status = next(zstatus_stream)
                self._latest = zone_status

            except (RequestsConnectionError, StopIteration):
                logging.warning("StatusLogger: Could not reach server!")
                if not self._running:
                    break
                sleep(1)
                zstatus_stream = self._api.get_zone_status_stream()

        self._running = False

    @property
    def is_running(self):
        return self._running

    def latest_statuses(self, stream_id) -> Dict[str, codecs.ZoneStatus]:
        """Returns the latest cached list of ZoneStatuses for that stream_id"""
        latest = self._latest
        if stream_id not in latest:
            return {}
        return latest[stream_id]

    def close(self):
        """Close the status polling thread"""
        self._running = False
        self.join()
