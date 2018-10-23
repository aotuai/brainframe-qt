import logging
from typing import Union, List, Dict
from io import BytesIO

import requests
import ujson
from PIL import Image
import cv2
import numpy as np

from brainframe.shared.singleton import Singleton
from brainframe.client.api.streaming import SyncedStreamReader
from brainframe.client.api.codecs import (
    Alert,
    Codec,
    EngineConfiguration,
    StreamConfiguration,
    Zone,
    ZoneStatus,
    Identity,
    PluginOption
)
from brainframe.client.api import api_errors
from brainframe.client.api.streaming import StreamManager
from brainframe.shared import error_kinds
from brainframe.client.api.status_poller import StatusPoller


def _make_api_error(resp_content):
    """Makes the corresponding error for this response.

    :param resp_content: The HTTP response to inspect for info
    :return: An error that can be thrown describing this failure
    """
    if len(resp_content) == 0:
        kind = error_kinds.UNKNOWN
        description = ("A failure happened but the server did not respond "
                       "with a proper error")
    else:
        resp_content = ujson.loads(resp_content)
        kind = resp_content["title"]
        description = resp_content["description"]

    if kind not in api_errors.kind_to_error_type:
        return api_errors.UnknownError(description)
    else:
        return api_errors.kind_to_error_type[kind](description)


class API:
    """The class instance of API
    If server_url is not used in constructor, set_url MUST be used.
    """
    # For testing purposes
    get = staticmethod(requests.get)
    put = staticmethod(requests.put)
    delete = staticmethod(requests.delete)

    def __init__(self, server_url=None):
        self._server_url = server_url

        # These are evaluated lazily
        self._stream_manager = None
        self._status_poller = None

    def set_url(self, server_url):
        self._server_url = server_url

    def get_status_poller(self) -> StatusPoller:
        """Returns the singleton StatusPoller object"""
        if self._status_poller is None or not self._status_poller.is_running:
            self._status_poller = StatusPoller(self, 33)
        return self._status_poller

    def get_stream_manager(self) -> StreamManager:
        """Returns the singleton StreamManager object"""
        if self._stream_manager is None:
            self._stream_manager = StreamManager(self.get_status_poller())
        return self._stream_manager

    # Stream Configuration
    def get_stream_configurations(self) -> List[StreamConfiguration]:
        """Get all StreamConfigurations that currently exist.

        :return: [StreamConfiguration, StreamConfiguration, ...]
        """
        req = "/api/streams/"
        data = self._get(req)

        configs = [StreamConfiguration.from_dict(d) for d in data]
        return configs

    def set_stream_configuration(self, stream_configuration) \
            -> Union[None, StreamConfiguration]:
        """Update an existing stream configuration or create a new one
        If creating a new one, the stream_configuration.id will be None
        :param stream_configuration: StreamConfiguration
        :return: StreamConfiguration, initialized with an ID
        """
        req = "/api/streams/"
        data = self._put_codec(req, stream_configuration)
        config = StreamConfiguration.from_dict(data)
        return config

    def delete_stream_configuration(self, stream_id):
        """Deletes a stream configuration with the given ID. Also stops
        analysis if analysis was running and closes the stream.

        :param stream_id: The ID of the stream to delete
        """
        req = f"/api/streams/{stream_id}"
        self._delete(req)
        if self._stream_manager is not None:
            self._stream_manager.close_stream_by_id(stream_id)

    # Stream Controls
    def get_stream_reader(self, stream_config: StreamConfiguration) \
            -> Union[None, SyncedStreamReader]:
        """Get the SyncedStreamReader for the given stream_id.

        :param stream_config: The stream configuration to open.
        :return: A SyncedStreamReader object OR None, if the server was unable
            to open a stream.
        """
        req = f"/api/streams/{stream_config.id}/url"
        try:
            url = self._get(req)
        except api_errors.StreamNotFoundError:
            logging.warning("API: Requested stream that doesn't exist!")
            return None

        logging.info("API: Opening stream on url " + url)

        pipeline = None
        if "pipeline" in stream_config.parameters:
            pipeline = stream_config.parameters["pipeline"]
        return self.get_stream_manager().start_streaming(
            stream_config.id, url, pipeline)

    # Setting server analysis tasks
    def start_analyzing(self, stream_id) -> bool:
        """
        Tell the server to set this stream config to active, and start analysis
        :param stream_id:
        :return: True or False if the server was able to start analysis on that
        stream. It could fail because: unable to start stream, or license
        restrictions.
        """
        req = f"/api/streams/{stream_id}/analyze"
        resp = self._put_json(req, 'true')
        return resp

    def stop_analyzing(self, stream_id):
        """Tell the server to close analyzing a particular stream
        :param stream_id:
        :return:
        """
        req = f"/api/streams/{stream_id}/analyze"
        self._put_json(req, 'false')

    # Get Analysis
    def get_latest_zone_statuses(self) -> Dict[int, List[ZoneStatus]]:
        """Get all ZoneStatuses
        This method gets ALL of the latest processed zone statuses for every
        zone for every stream. The call is intentionally broad and large so as
        to lower the overhead of pinging the server and waiting for a return.

        All active streams will have a key in the output dict.
        :return:
        {stream_id1: [ZoneStatus, ZoneStatus], stream_id2: [ZoneStatus]}
        """
        req = "/api/streams/status/"
        data = self._get(req)

        # Convert ZoneStatuses to Codecs
        out = {int(s_id): [ZoneStatus.from_dict(status)
                           for status in statuses]
               for s_id, statuses in data.items()}
        return out

    # Alerts
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
            img_bytes = self._get_raw(req)
            return cv2.imdecode(np.fromstring(img_bytes, np.uint8),
                                cv2.IMREAD_COLOR)
        except api_errors.FrameNotFoundForAlertError:
            return None

    # Backend Capabilities
    def get_engine_configuration(self) -> EngineConfiguration:
        """Returns the capabilities of the machine learning engine on the
        server.

        Currently, it can tell you:
            The types of objects that can be detected
            The types of attributes that can be detected for each object.

        :return: EngineConfiguration
        """
        req = "/api/engine-configuration"
        resp = self._get(req)
        return EngineConfiguration.from_dict(resp)

    def get_zones(self, stream_id) -> List[Zone]:
        """Returns a list of Zone's associated with that stream"""
        req = f"/api/streams/{stream_id}/zones"
        data = self._get(req)
        zones = [Zone.from_dict(j) for j in data]
        return zones

    def get_zone(self, stream_id, zone_id) -> Zone:
        """Get a specific zone.
        :param stream_id: The ID of the stream that the desired zone is for
        :param zone_id: The ID of the zone to get
        """
        data = self.get_zones(stream_id)
        zones = [zone for zone in data if zone.id == zone_id]
        assert len(zones) != 0, ("A zone with that stream_id and zone_id could"
                                 " not be found!")
        return zones[0]

    def set_zone(self, stream_id: int, zone: Zone):
        """Update or create a zone. If the Zone doesn't exist, the zone.id
        must be None. An initialized Zone with an ID will be returned.
        :param stream_id: The stream_id that this zone exists in
        :param zone: A Zone object
        :return: Zone, initialized with an ID
        """
        req = f"/api/streams/{stream_id}/zones"
        data = self._put_codec(req, zone)
        new_zone = Zone.from_dict(data)
        return new_zone

    def delete_zone(self, stream_id: int, zone_id: int):
        """Deletes a zone with the given ID.
        :param stream_id: The ID of the stream the zone is a part of
        :param zone_id: The ID of the zone to delete
        """
        req = f"/api/streams/{stream_id}/zones/{zone_id}"
        self._delete(req)

    # Identities
    def get_identity(self, identity_id: int) -> Identity:
        """Gets the identity with the given ID.
        :param identity_id: The ID of the identity to get
        :return: Identity
        """
        req = f"/api/identities/{identity_id}"
        identity = self._get(req)

        return Identity.from_dict(identity)

    def get_identities(self, unique_name=None) -> List[Identity]:
        """Returns all identities from the server.
        :return: List of identities
        """
        req = f"/api/identities"
        params = {"unique_name": unique_name} if unique_name else None
        identities = self._get(req, params=params)
        identities = [Identity.from_dict(d) for d in identities]

        return identities

    def set_identity(self, identity: Identity) -> Identity:
        """Updates or creates an identity. If the identity does not already
        exist, identity.id must be None. The returned identity will have an
        assigned ID.
        :param identity: The identity to save or create
        :return: the saved identity
        """
        req = f"/api/identities"
        saved = self._put_codec(req, identity)
        return Identity.from_dict(saved)

    def new_identity_image(self, identity_id: int, class_name: str,
                           image: bytes) -> int:
        """Saves and encodes an image under the identity with the given ID.

        :param identity_id: Identity to associate the image with
        :param class_name: The type of object this image shows and should be
            encoded for
        :param image: The image to save
        :return: The image ID
        """
        req = f"/api/identities/{identity_id}/classes/{class_name}/images"

        # Try to figure out the image type. If we can't figure it out, send it
        # as raw data to the server in case the server supports it

        try:
            pil_image = Image.open(BytesIO(image))

            if pil_image.format == "JPEG":
                mime_type = "image/jpeg"
            elif pil_image.format == "PNG":
                mime_type = "image/png"
            else:
                mime_type = "application/octet-stream"
        except IOError:
            # TODO(Tyler Compton): This failure mode is stupid but I don't want
            # two ways for this call to fail when an invalid image is passed to
            # it. Figure out a better way.
            mime_type = "application/octet-stream"

        image_id = self._put_raw(req, image, mime_type)
        return image_id

    def new_identity_vector(self, identity_id: int, class_name: str,
                            vector: List[float]) -> int:
        """Saves the given vector under the identity with the given ID. In this
        case, a vector is simply a list of one or more numbers that describe
        some object in an image.

        :param identity_id: Identity to associate the vector with
        :param class_name: The type of object this vector describes
        :param vector: The vector to save
        :return: The vector ID
        """
        req = f"/api/identities/{identity_id}/classes/{class_name}/vectors"

        return self._put_json(req, ujson.dumps(vector))

    def get_identity_image(self, identity_id: int, class_name: str,
                           image_id: int) -> np.ndarray:
        """Returns the image with the given image ID.

        :param identity_id: The ID of the identity that the image is associated
            with
        :param class_name: The class name that this image was encoded for
        :param image_id: The ID of the image
        :return: The image as loaded by OpenCV
        """
        req = (f"/api/identities/{identity_id}"
               f"/classes/{class_name}"
               f"/images/{image_id}")
        image_bytes = self._get_raw(req)

        return cv2.imdecode(np.fromstring(image_bytes, np.uint8),
                            cv2.IMREAD_COLOR)

    def get_image_ids_for_identity(self, identity_id, class_name) -> List[int]:
        """Returns all IDs for the identity with the given ID that are for
        encodings of the given class name.

        :param identity_id: The ID of the identity to look for images under
        :param class_name: The class name to look for images encoded for
        :return: List of image IDs
        """
        req = (f"/api/identities/{identity_id}"
               f"/classes/{class_name}"
               f"/images")
        image_ids = self._get(req)
        return image_ids

    def get_plugin_names(self) -> List[str]:
        """
        :return: The names of all available plugins
        """
        req = "/api/plugins"
        plugin_names = self._get(req)
        return plugin_names

    def get_plugin_options(self, plugin_name, stream_id=None) \
            -> Dict[str, PluginOption]:
        """Gets all available options for a plugin and their current
        configuration. See the documentation for the PluginOption codec for more
        info about global and stream level options and how they interact.

        :param plugin_name: The plugin to find options for
        :param stream_id: The ID of the stream. If this value is None, then the
            global options are returned for that plugin
        :return: A dict where the key is the option name and the value is the
            PluginOption
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/options"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/options"
        plugin_configs_json = self._get(req)
        return {name: PluginOption.from_dict(pc)
                for name, pc in plugin_configs_json.items()}

    def set_plugin_option_vals(self, *, plugin_name, stream_id=None,
                               option_vals: Dict[str, object]):
        """Sets option values for a plugin.

        :param plugin_name: The name of the plugin whose options to set
        :param stream_id: The ID of the stream, if these are stream-level
            options. If this value is None, then the global options are set
        :param option_vals: A dict where the key is the name of the option to
            set, and the value is the value to set that option to
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/options"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/options"

        option_values_json = ujson.dumps(option_vals)
        self._put_json(req, option_values_json)

    def is_plugin_active(self, plugin_name, stream_id=None) -> bool:
        """Returns true if the plugin is active. If a plugin is not marked as
        active, it will not run. Like plugin options, this can be configured
        globally and on a per-stream level.

        :param plugin_name: The name of the plugin to get activity for
        :param stream_id: The ID of the stream, if you want the per-stream
            active setting
        :return: True if the plugin is active
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/active"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/active"
        plugins_active = self._get(req)
        return plugins_active

    def set_plugin_active(self, *, plugin_name, stream_id=None, active: bool):
        """Sets whether or not the plugin is active. If a plugin is active, it
        will be run on frames.

        :param plugin_name: The name of the plugin to set activity for
        :param stream_id: The ID of the stream, if you want to set the
            per-stream active setting
        :param active: True if the plugin should be set to active
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/active"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/active"

        active_json = ujson.dumps(active)

        self._put_json(req, active_json)

    def close(self):
        """Clean up the API. It may no longer be used after this call."""
        if self._status_poller is not None:
            self._status_poller.close()
            self._status_poller = None
        if self._stream_manager is not None:
            self._stream_manager.close()
            self._stream_manager = None

    # Private Functions
    def _get(self, api_url, params=None):
        """Send a GET request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
        of a dict, {"key": "value", ...} key and val must be a string
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.get(self._full_url(api_url), params=params)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _get_raw(self, api_url, params=None):
        """Send a GET request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the url. In the format
        of a dict, {"key": "value", ...} key and val must be a string
        :return: The raw bytes of the response
        """
        resp = self.get(self._full_url(api_url), params=params)
        if not resp.ok:
            raise _make_api_error(resp.content)

        return resp.content

    def _put_raw(self, api_url, data: bytes, content_type: str):
        """Send a PUT request to the given URL.
        :param api_url: The /api/blah/blah to append to the base url
        :param data: The raw data to send
        :param content_type: The mime type of the data being sent
        :return: The JSON response as a dict, or None of none was sent
        """
        resp = self.put(self._full_url(api_url),
                        data=data,
                        headers={'content-type': content_type})
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _put_codec(self, api_url, codec: Codec):
        """Send a PUT request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param codec: A codec to convert to JSON and send
        :return: The JSON response as a dict, or None if none was sent
        """
        data = codec.to_json()
        resp = self.put(self._full_url(api_url), data=data)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _put_json(self, api_url, json):
        """Send a PUT request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param json: Preformatted JSON to send
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.put(self._full_url(api_url), data=json)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _delete(self, api_url, params=None):
        """Sends a DELETE request to the given URL.
        :param api_url: The /api/blah/blah to append to the base_url
        :param params: The "query_string" to add to the URL. Must be a
          str-to-str dict
        :return: The JSON response as a dict, or None if none was sent
        """
        resp = self.delete(self._full_url(api_url), params=params)
        if not resp.ok:
            raise _make_api_error(resp.content)

        if resp.content:
            return ujson.loads(resp.content)
        return None

    def _full_url(self, api_url):
        url = "{base_url}{api_url}".format(
            base_url=self._server_url,
            api_url=api_url)
        return url
