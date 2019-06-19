from typing import List, Optional, Tuple

import numpy as np
import ujson

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Alert
from brainframe.client.api import image_utils
from brainframe.client.api import api_errors


class AlertStubMixin(Stub):
    """Provides stubs for calling APIs related to controlling and getting
    alerts.
    """

    def get_unverified_alerts(self, stream_id,
                              limit: Optional[int] = None,
                              offset: Optional[int] = None) \
            -> Tuple[List[Alert], int]:
        """Gets all alerts that have not been verified or rejected

        :param stream_id: The stream ID to get unverified alerts for
        :param limit: The maximum number of alerts to return. If None, no limit
            will be applied
        :param offset: The offset from the most recent alerts to return. This
            is only useful when providing a limit.
        :return:  A list of alerts, and the total number of alerts that
            fit this criteria, ignoring pagination (the limit and offset)
        """
        req = "/api/alerts"

        params = {"stream_id": stream_id}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        data, headers = self._get_with_headers(req, params=params)
        alerts = [Alert.from_dict(a) for a in data]

        total_count = int(headers["Total-Count"])

        return alerts, total_count

    def set_alert_verification(self, alert_id, verified_as: bool):
        """Sets an alert verified as True or False.

        :param alert_id: The ID of the alert to set
        :param verified_as: Set verification to True or False
        :return: The modified Alert
        """
        req = f"/api/alerts/{alert_id}"
        self._put_json(req, ujson.dumps(verified_as))

    def get_alert_frame(self, alert_id: int) -> Optional[np.ndarray]:
        """Returns the frame saved for this alert, or None if no frame is
        recorded for this alert.

        :param alert_id: The ID of the alert to get a frame for.
        :return: The image as loaded by OpenCV, or None
        """
        req = f"/api/alerts/{alert_id}/frame"
        try:
            img_bytes, _ = self._get_raw(req)
            return image_utils.decode(img_bytes)
        except api_errors.FrameNotFoundForAlertError:
            return None
