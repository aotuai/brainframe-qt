import logging
from threading import RLock, Thread
from time import sleep
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

import requests

from brainframe.client.api import api_errors, codecs
from brainframe.client.api.stubs.zone_statuses import \
    ZONE_STATUS_STREAM_TYPE, ZONE_STATUS_TYPE

if TYPE_CHECKING:
    from brainframe.client.api import API


class StatusReceiver(Thread):
    """This solves the problem that multiple UI elements will want to know the
    latest ZoneStatuses for any given stream."""

    ZONE_STATUS_STREAM_TIMEOUT = 10
    """The timeout in seconds before reinitializing a connection to the server. 
    If none, the zonestatus stream will wait forever even if there are no 
    results, making the thread potentially never check if it should be 
    closing.
    """

    def __init__(self, api: 'API'):
        """
        :param api: An API() object for interacting with the BrainFrame REST
            api
        """
        super().__init__(name="StatusReceiverThread")
        self._api = api

        self._listeners: List[Callable[[ZONE_STATUS_TYPE], Any]] = []
        self._listener_lock = RLock()

        self._latest_statuses = {}

        # no cleanup code so we can just die when the main thread dies
        self.daemon = True

        self._running = True
        self.start()

    def run(self):
        """Opens a connection with BrainFrame to receive ZoneStatus objects.
        Then, alerts any event handlers of new objects."""
        self._running = True
        zone_status_stream: Optional[ZONE_STATUS_STREAM_TYPE] = None

        while self._running:
            if zone_status_stream is None:
                zone_status_stream = self._api.get_zone_status_stream(
                    timeout=self.ZONE_STATUS_STREAM_TIMEOUT)
            try:
                zone_statuses = next(zone_status_stream)
            except (StopIteration,
                    requests.exceptions.RequestException,
                    api_errors.UnknownError) as ex:

                # Catch any 502 errors that happen during server restart
                if isinstance(ex, api_errors.UnknownError) \
                        and ex.status_code != 502:
                    raise

                if not self._running:
                    break

                zone_status_stream = None

                logging.warning(f"StatusLogger: Could not reach server: {ex}")
                sleep(1)
            else:
                self._ingest_zone_statuses(zone_statuses)

        self._running = False

    def add_listener(self, listener: Callable[[ZONE_STATUS_TYPE], Any]):
        with self._listener_lock:
            self._listeners.append(listener)

    @property
    def is_running(self) -> bool:
        return self._running

    def _ingest_zone_statuses(self, zone_statuses: ZONE_STATUS_TYPE):
        self._latest_statuses = zone_statuses

        with self._listener_lock:
            for listener in self._listeners:
                listener(zone_statuses)

    # TODO: Remove usages of this
    def latest_statuses(self, stream_id: int) -> Dict[str, codecs.ZoneStatus]:
        """Returns the latest cached list of ZoneStatuses for that stream_id,
        or any empty dict if none are cached"""
        return self._latest_statuses.get(stream_id, {})

    def close(self) -> None:
        """Close the status receiving thread"""
        self._running = False
        self.join()
