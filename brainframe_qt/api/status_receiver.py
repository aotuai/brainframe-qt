import logging
from queue import Empty, Full, Queue
from threading import RLock, Thread
from time import sleep
from typing import Dict, Set, TYPE_CHECKING

import requests

from brainframe.client.api import api_errors, codecs
from brainframe.client.api.stubs.zone_statuses import ZONE_STATUS_TYPE

if TYPE_CHECKING:
    from brainframe.client.api import API


class ZoneStatusQueue(Queue):
    """This is used by the StatusReceiver to pass events to the UI"""

    def __init__(self, maxsize=100):
        super().__init__(maxsize)

    def put(self, zone_status: ZONE_STATUS_TYPE, _block=False, _timeout=None):
        try:
            super().put(zone_status, block=False)
        except Full:
            pass

    def clear(self):
        while not self.empty():
            try:
                self.get(False)
            except Empty:
                continue
            self.task_done()


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

        self.status_queues: Set[ZoneStatusQueue] = set()
        self._status_queues_lock = RLock()

        self._latest_statuses = {}
        self._running = False

        self.start()

    def run(self):
        """Opens a connection with BrainFrame to receive ZoneStatus objects.
        Then, alerts any event handlers of new objects."""
        self._running = True
        zone_status_stream = self._api.get_zone_status_stream()

        while self._running:
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

                logging.warning(f"StatusLogger: Could not reach server: {ex}")
                sleep(1)
                zone_status_stream = self._api.get_zone_status_stream()
            else:
                self._ingest_zone_statuses(zone_statuses)

        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def subscribe(self, listener: ZoneStatusQueue):
        with self._status_queues_lock:
            self.status_queues.add(listener)

    def unsubscribe(self, listener: ZoneStatusQueue):
        with self._status_queues_lock:
            self.status_queues.remove(listener)

    def _ingest_zone_statuses(self, zone_status: ZONE_STATUS_TYPE):
        with self._status_queues_lock:
            for queue in self.status_queues:
                queue.put(zone_status)
        self._latest_statuses = zone_status

    # TODO: Remove usages of this
    def latest_statuses(self, stream_id: int) -> Dict[str, codecs.ZoneStatus]:
        """Returns the latest cached list of ZoneStatuses for that stream_id,
        or any empty dict if none are cached"""
        return self._latest_statuses.get(stream_id, {})

    def close(self) -> None:
        """Close the status receiving thread"""
        self._running = False
        self.join()
