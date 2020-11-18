from typing import Dict, Optional
from uuid import UUID, uuid4

import numpy as np
from brainframe.api.bf_codecs import ZoneStatus, Zone

from brainframe.client.api_utils.detection_tracks import DetectionTrack
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

    def sync(
            self, *,
            frame_tstamp: float,
            frame: np.ndarray,
            zone_statuses: Dict[str, ZoneStatus]
    ) -> Optional[ZoneStatusFrame]:
        """Input is frame_tstamp, frame, statuses and returns ZoneStatusFrames
        where the ZoneStatuses and frames are synced up."""

        self.buffer.add_frame(
            ZoneStatusFrame(
                frame=frame,
                tstamp=frame_tstamp,
                zone_statuses=None,
                tracks=None
            )
        )

        # Analysis still spinning up. Skip
        if not len(zone_statuses):
            if self.buffer.is_full and not self.buffer.needs_guaranteed_space:
                # Pop the unpaired frame anyways to ensure no memory leak and
                # so the client can show a frame, even if there's nothing to
                # render
                self.latest_processed = self.buffer.pop_oldest()
            # This returns None if the buffer isn't full and no zone statuses
            # have ever been returned by the server. It returns a
            # ZoneStatusFrame with zone_statuses=None in the case when the
            # buffer is already full, but the server still has never returned
            # a zone status.
            return self.latest_processed

        # Get timestamp off of default zone's status (all should be equal)
        status_tstamp = zone_statuses[Zone.FULL_FRAME_ZONE_NAME].tstamp

        # Check if this is a fresh zone_status or not
        if self.last_status_tstamp != status_tstamp:
            # Catch buffer up to the previous inference frame (get rid of
            # frames that the client will never render because it's running
            # too far behind)
            self.buffer.pop_until(self.last_status_tstamp)

            self.last_status_tstamp = status_tstamp

            # Iterate over all new detections, and add them to their tracks
            dets = zone_statuses[Zone.FULL_FRAME_ZONE_NAME].within
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

        # Pop a frame if we're over the combined buffer max, but we also have
        # more frames than the guaranteed minimum
        if popped_frame is None:
            if self.buffer.is_full and not self.buffer.needs_guaranteed_space:
                popped_frame = self.buffer.pop_oldest()
                popped_frame.frame_metadata.client_buffer_full = True

        # If we have a frame using any means, use it
        if popped_frame is not None:
            self.latest_processed = self._apply_statuses_to_frame(
                frame=popped_frame,
                statuses=zone_statuses,
                tracks=self.tracks,
            )

            self.last_used_zone_statuses = zone_statuses

        # Prune DetectionTracks that haven't had a detection in a while
        for uuid, track in list(self.tracks.items()):
            detection_lapse = frame_tstamp - track.latest_tstamp
            if detection_lapse > self.MAX_CACHE_TRACK_SECONDS:
                del self.tracks[uuid]

        return self.latest_processed

    # noinspection PyMethodMayBeStatic
    def _apply_statuses_to_frame(self, frame: ZoneStatusFrame,
                                 statuses: Dict[str, ZoneStatus],
                                 tracks: Dict[UUID, DetectionTrack]) \
            -> ZoneStatusFrame:

        # Get timestamp off of default zone's status (all should be equal)
        status_tstamp = statuses[Zone.FULL_FRAME_ZONE_NAME].tstamp

        # Get a list of DetectionTracks that had a detection for
        # this timestamp
        relevant_dets = [dt.copy() for dt in tracks.values()
                         if dt.latest_tstamp == status_tstamp]

        applied_frame = ZoneStatusFrame(
            frame=frame.frame,
            tstamp=frame.tstamp,
            zone_statuses=statuses,
            tracks=relevant_dets,
            frame_metadata=frame.frame_metadata
        )

        return applied_frame
