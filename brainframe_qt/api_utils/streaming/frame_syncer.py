from datetime import timedelta
from typing import Dict, Optional
from uuid import UUID, uuid4

from brainframe.api.bf_codecs import ZoneStatus, Zone

from brainframe_qt.api_utils.detection_tracks import DetectionTrack
from .frame_buffer import SyncedFrameBuffer
from .zone_status_frame import ZoneStatusFrame


class FrameSyncer:
    """Keeps frames synced with detections and tracks"""
    MAX_CACHE_TRACK_SECONDS = 30

    def __init__(self):
        self.last_status_tstamp: float = -1
        """Keep track of the timestamp of the last new ZoneStatus that was 
        received."""

        self.last_used_zone_statuses: Optional[Dict[str, ZoneStatus]] = None
        """The last zone status object that was put into a processed frame.
        Useful for identifying if a ProcessFrame has new information, or is 
        simply paired with old information."""

        self.latest_processed = None
        """Keeps track of the latest ZoneStatusFrame with information"""

        self.buffer = SyncedFrameBuffer()
        """Holds a queue of empty ZoneStatusFrames"""

        self.tracks: Dict[UUID, DetectionTrack] = {}
        """Keep a dict of Detection.track_id: DetectionTrack of all detections
        that are ongoing. Then, every once in a while, prune DetectionTracks 
        that haven't gotten updates in a while."""

    def sync(self, *,
             latest_frame: ZoneStatusFrame,
             latest_zone_statuses: Dict[str, ZoneStatus]) \
            -> Optional[ZoneStatusFrame]:
        """Sync frames with statuses

        Input is a ZoneStatusFrame with a frame and tstamp, and the latest
        ZoneStatuses

        Returns a ZoneStatusFrame with the statuses synced to its frame, or
        None if no frame to sync to."""

        self.buffer.add_frame(latest_frame)

        # Analysis still spinning up. Skip
        if not len(latest_zone_statuses):
            if not self.buffer.is_full or self.buffer.needs_guaranteed_space:
                # Keep building buffer; nothing to do
                return None

            # Pop the unpaired frame anyways to ensure no memory leak and
            # so the client can show a frame, even if there's nothing to
            # render
            popped_frame = self.buffer.pop_oldest()
            popped_frame.frame_metadata.client_buffer_full = True
            popped_frame.frame_metadata.no_analysis = True

            # This returns None if the buffer isn't full and no zone statuses
            # have ever been returned by the server. It returns a
            # ZoneStatusFrame with zone_statuses=None in the case when the
            # buffer is already full, but the server still has never returned
            # a zone status.
            self.latest_processed = popped_frame
            return popped_frame

        # Get timestamp off of default zone's status (all should be equal)
        status_tstamp = latest_zone_statuses[Zone.FULL_FRAME_ZONE_NAME].tstamp

        # Check if this is a fresh zone_status or not
        if self.last_status_tstamp != status_tstamp:
            # Catch buffer up to the previous inference frame (get rid of
            # frames that the client will never render because it's running
            # too far behind)
            self.buffer.pop_until(self.last_status_tstamp)

            self.last_status_tstamp = status_tstamp

            # Iterate over all new detections, and add them to their tracks
            dets = latest_zone_statuses[Zone.FULL_FRAME_ZONE_NAME].within
            for det in dets:
                # Create new tracks where necessary
                track_id = det.track_id if det.track_id else uuid4()

                if det.track_id not in self.tracks:
                    self.tracks[track_id] = DetectionTrack()
                self.tracks[track_id].add_detection(det, status_tstamp)

        # If we have a zone status/inference result newer than the latest
        # received frame, associate the buffer's oldest frame with the zone
        # status
        popped_frame = self.buffer.pop_if_older(self.last_status_tstamp)
        if popped_frame is not None:
            analysis_latency = status_tstamp - popped_frame.tstamp
            analysis_latency = timedelta(seconds=analysis_latency)
            popped_frame.frame_metadata.analysis_latency = analysis_latency

        # Pop a frame if we're over the combined buffer max, but we also have
        # more frames than the guaranteed minimum
        else:
            if self.buffer.is_full and not self.buffer.needs_guaranteed_space:
                popped_frame = self.buffer.pop_oldest()
                popped_frame.frame_metadata.client_buffer_full = True

        # If we have a frame using any means, use it
        if popped_frame is not None:
            self._apply_statuses_to_frame(
                frame=popped_frame,
                statuses=latest_zone_statuses,
                tracks=self.tracks,
            )

            self.last_used_zone_statuses = latest_zone_statuses

        # Prune DetectionTracks that haven't had a detection in a while
        self._prune_detection_tracks(latest_frame.tstamp)

        self.latest_processed = popped_frame
        return popped_frame

    # noinspection PyMethodMayBeStatic
    def _apply_statuses_to_frame(self, *, frame: ZoneStatusFrame,
                                 statuses: Dict[str, ZoneStatus],
                                 tracks: Dict[UUID, DetectionTrack]) \
            -> None:

        # Get timestamp off of default zone's status (all should be equal)
        status_tstamp = statuses[Zone.FULL_FRAME_ZONE_NAME].tstamp

        # Get a list of DetectionTracks that had a detection for
        # this timestamp
        relevant_dets = [dt.copy() for dt in tracks.values()
                         if dt.latest_tstamp == status_tstamp]

        frame.zone_statuses = statuses
        frame.tracks = relevant_dets

    def _prune_detection_tracks(self, frame_tstamp: float) -> None:
        for uuid, track in list(self.tracks.items()):
            detection_lapse = frame_tstamp - track.latest_tstamp
            if detection_lapse > self.MAX_CACHE_TRACK_SECONDS:
                del self.tracks[uuid]
