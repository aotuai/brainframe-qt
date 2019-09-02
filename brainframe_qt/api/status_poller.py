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
        self._session = requests.Session()

        # Get something before starting the thread
        self._latest = self._api.get_latest_zone_statuses()
        self._running = True
        self.start()

    def run(self):
        """Polls BrainFrame for ZoneStatuses at a constant rate"""
        self._running = True
        call_time = 0

        zstatus_stream = self._get_zonestatus_iterator()
        while self._running:

            try:
                start = time()
                next_line = next(zstatus_stream)
                print("Boutta parse", next_line)
                if next_line == b'':
                    logging.warning("ZoneStatus pipe seemingly broke")
                    zstatus_stream = self._get_zonestatus_iterator()
                    continue

                self._latest = ujson.loads(next_line)
                print("LAtest", self._latest)
                call_time = time() - start
            except RequestsConnectionError:
                logging.warning("StatusLogger: Could not reach server!")
                sleep(2)

            print("Call time", call_time)

        self._running = False

    def _get_zonestatus_iterator(self):
        """This is used to initiate a conection to the servers zone status
        multipart streamed endpoint"""
        url = f"{self._api._server_url}/api/streams/status?streamed=1"
        zstatus_stream = self._session.get(url, stream=True).iter_lines(
            delimiter=b"\r\n")
        return zstatus_stream

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
        self._session.close()
        self.join()
