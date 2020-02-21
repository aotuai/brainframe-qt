import logging
from threading import Thread
from time import sleep
from typing import Dict, TYPE_CHECKING

import requests

from brainframe.client.api import api_errors, codecs

if TYPE_CHECKING:
    from brainframe.client.api import API


class StatusPoller(Thread):
    """This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream."""

    def __init__(self, api: 'API'):
        """
        :param api: An API() object for interacting with the BrainFrame REST
            api
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
        zone_status_stream = self._api.get_zone_status_stream()

        while self._running:
            try:
                zone_status = next(zone_status_stream)
                self._latest = zone_status

            except (StopIteration,
                    requests.exceptions.RequestException,
                    api_errors.UnknownError) as ex:
                # Catch any 502 errors that happen during server restart
                if ex is api_errors.UnknownError and ex.status_code != 502:
                    raise
                logging.warning(f"StatusLogger: Could not reach server: {ex}")

                if not self._running:
                    break

                sleep(1)
                zone_status_stream = self._api.get_zone_status_stream()

        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def latest_statuses(self, stream_id: int) -> Dict[str, codecs.ZoneStatus]:
        """Returns the latest cached list of ZoneStatuses for that stream_id,
        or any empty dict if none are cached"""
        return self._latest.get(stream_id, {})

    def close(self) -> None:
        """Close the status polling thread"""
        self._running = False
        self.join()
