from typing import Any, Dict

from PyQt5.QtCore import QObject

from brainframe.client.api import api
from brainframe.client.api.zss_pubsub import zss_publisher, ZSSDataType, \
    ZSSTopic
from brainframe.client.api.codecs import Alert
from brainframe.client.ui.resources import QTAsyncWorker


class _QTAsyncAPIPubsub(QObject):

    @staticmethod
    def set_alert_verification(thread_owner: QObject,
                               alert: Alert, verified_as: bool,
                               on_success=None, on_error=None):

        def async_func():
            api.set_alert_verification(alert.id, verified_as)

        def on_success_cb(api_result):
            # Change the client-stored alert's data
            alert.verified_as = verified_as

            # Call the callback and publish the data on the pubsub
            _QTAsyncAPIPubsub._publish_on_success(
                on_success, api_result,
                {ZSSTopic.ALERTS: [alert]})

        worker = QTAsyncWorker(thread_owner, async_func,
                               on_success=on_success_cb,
                               on_error=on_error)
        worker.start()

    # @async_pubsub(api.set_alert_verification, zss_publisher.Topic.ALERTS)
    # def set_alert_verification2(self, alert: Alert, verified_as: bool):
    #     alert.verified_as = verified_as

    @staticmethod
    def _publish_on_success(on_success: QTAsyncWorker.CallbackT,
                            api_result: Any,
                            publish_message: Dict[ZSSTopic,
                                                  ZSSDataType]):

        # Call the original callback if it was set
        if on_success is not None:
            on_success(api_result)

        # Publish the contents of the change on the pubsub system
        zss_publisher.publish(publish_message)


async_api_pubsub = _QTAsyncAPIPubsub
