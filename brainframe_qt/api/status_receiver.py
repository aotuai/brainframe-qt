import logging
from threading import Thread
from time import sleep
from typing import Dict, TYPE_CHECKING

import requests

from brainframe.client.api import api_errors, codecs

if TYPE_CHECKING:
    from brainframe.client.api import API


class StatusReceiver(Thread):
    """This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream."""

    def __init__(self, api: 'API'):
        """
        :param api: An API() object for interacting with the BrainFrame REST
            api
        """
        super().__init__(name="StatusReceiverThread")
        self._api = api

        # Get something before starting the thread
        self._latest_statuses = {}
        self._running = True
        self.start()

    def run(self):
        """Opens a connection with BrainFrame to receive ZoneStatus objects.
        Then, alerts any event handlers of new objects."""
        self._running = True
        zone_status_stream = self._api.get_zone_status_stream()

        while self._running:
            try:
                zone_status = next(zone_status_stream)
                self._latest_statuses = zone_status

            except (StopIteration,
                    requests.exceptions.RequestException,
                    api_errors.UnknownError) as ex:

                # Catch any 502 errors that happen during server restart
                if isinstance(ex, api_errors.UnknownError) \
                        and ex.status_code != 502:
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
        return self._latest_statuses.get(stream_id, {})

    def close(self) -> None:
        """Close the status receiving thread"""
        self._running = False
        self.join()