from enum import Flag, auto
from typing import List, Optional, Tuple

import numpy as np
import ujson

from brainframe.client.api import api_errors, image_utils
from brainframe.client.api.codecs import Alert
from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT


class AlertStubMixin(BaseStub):
    """Provides stubs for calling APIs related to controlling and getting
    alerts.
    """

    class AlertVerificationQueryType(Flag):
        UNVERIFIED = auto()
        TRUE = auto()
        FALSE = auto()
        VERIFIED = TRUE | FALSE
        NO_FALSE_POSITIVES = UNVERIFIED | TRUE
        NO_TRUE_POSITIVES = UNVERIFIED | FALSE
        ALL = UNVERIFIED | TRUE | FALSE

        @property
        def query_repr(self):
            values = []
            if self & self.UNVERIFIED:
                values.append("unverified")
            if self & self.TRUE:
                values.append("true")
            if self & self.FALSE:
                values.append("false")
            return ','.join(values)

    def get_alerts(self,
                   stream_id: Optional[int] = None,
                   zone_id: Optional[int] = None,
                   alarm_id: Optional[int] = None,
                   verification: Optional[AlertVerificationQueryType]
                   = AlertVerificationQueryType.ALL,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None,
                   timeout=DEFAULT_TIMEOUT) \
            -> Tuple[List[Alert], int]:
        """Gets all alerts that match a query

        :param stream_id: The ID of the stream to get alerts for
        :param zone_id: The ID of the zone to get alerts for
        :param alarm_id: The ID of the alarm to get alerts for
        :param verification: The verification states of the alerts
        :param limit: The maximum number of alerts to return. If None, no limit
            will be applied
        :param offset: The offset from the most recent alerts to return. This
            is only useful when providing a limit.
        :param timeout: The timeout to use for this request
        :return:  A list of alerts, and the total number of alerts that
            fit this criteria, ignoring pagination (the limit and offset)
        """
        req = "/api/alerts"

        params = {}
        if stream_id is not None:
            params["stream_id"] = stream_id
        if zone_id is not None:
            params["zone_id"] = zone_id
        if alarm_id is not None:
            params["alarm_id"] = alarm_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if verification is not self.AlertVerificationQueryType.ALL:
            params["verification"] = verification.query_repr

        data, headers = self._get_json(req, timeout, params=params)
        alerts = [Alert.from_dict(a) for a in data]

        total_count = int(headers["Total-Count"])

        return alerts, total_count

    def set_alert_verification(self, alert_id, verified_as: bool,
                               timeout=DEFAULT_TIMEOUT):
        """Sets an alert verified as True or False.

        :param alert_id: The ID of the alert to set
        :param verified_as: Set verification to True or False
        :param timeout: The timeout to use for this request
        :return: The modified Alert
        """
        req = f"/api/alerts/{alert_id}"
        self._put_json(req, timeout, ujson.dumps(verified_as))

    def get_alert_frame(self, alert_id: int,
                        timeout=DEFAULT_TIMEOUT) -> Optional[np.ndarray]:
        """Returns the frame saved for this alert, or None if no frame is
        recorded for this alert.

        :param alert_id: The ID of the alert to get a frame for.
        :param timeout: The timeout to use for this request
        :return: The image as loaded by OpenCV, or None
        """
        req = f"/api/alerts/{alert_id}/frame"
        try:
            img_bytes = self._get(req, timeout).content
            return image_utils.decode(img_bytes)
        except api_errors.FrameNotFoundForAlertError:
            return None
