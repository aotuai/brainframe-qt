from typing import List, Union

import cv2
import numpy as np
import ujson

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import Alert
from brainframe.client.api import api_errors


class AlertStubMixin(Stub):
    """Provides stubs for calling APIs related to controlling and getting
    alerts.
    """

    def get_unverified_alerts(self, stream_id, page=1) -> List[Alert]:
        """Gets all alerts that have not been verified or rejected

        :param stream_id: The stream ID to get unverified alerts for
        :param page: Which "page" of alerts to get. Alerts are paginated in
            sections of 100. The first page gets the first 100, the second page
            gets the second 100, and so on.
        :return:
        """
        req = "/api/alerts"
        data = self._get(req, params={"stream_id": str(stream_id),
                                      "page": str(page)})

        alerts = [Alert.from_dict(a) for a in data]
        return alerts

    def set_alert_verification(self, alert_id, verified_as: bool):
        """Sets an alert verified as True or False.

        :param alert_id: The ID of the alert to set
        :param verified_as: Set verification to True or False
        :return: The modified Alert
        """
        req = f"/api/alerts/{alert_id}"
        self._put_json(req, ujson.dumps(verified_as))

    def get_alert_frame(self, alert_id: int) -> Union[np.ndarray, None]:
        """Returns the frame saved for this alert, or None if no frame is
        recorded for this alert.

        :param alert_id: The ID of the alert to get a frame for.
        :return: The image as loaded by OpenCV, or None
        """
        req = f"/api/alerts/{alert_id}/frame"
        try:
            img_bytes, _ = self._get_raw(req)
            return cv2.imdecode(np.fromstring(img_bytes, np.uint8),
                                cv2.IMREAD_COLOR)
        except api_errors.FrameNotFoundForAlertError:
            return None
