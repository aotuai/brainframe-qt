from typing import Dict, List, Optional

import ujson

from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT
from brainframe.client.api.codecs import PluginOption, Plugin


class PluginStubMixin(BaseStub):
    """Provides stubs to call APIs to inspect and configure plugins."""

    def get_plugin(self, name,
                   timeout=DEFAULT_TIMEOUT) -> Plugin:
        """
        :param name: The name of the plugin to get
        :param timeout: The timeout to use for this request
        :return: Plugin with the given name
        """
        req = f"/api/plugins/{name}"
        plugin, _ = self._get_json(req, timeout)
        return Plugin.from_dict(plugin)

    def get_plugins(self, timeout=DEFAULT_TIMEOUT) -> List[Plugin]:
        """
        :param timeout: The timeout to use for this request
        :return: All available plugins
        """
        req = "/api/plugins"
        plugins, _ = self._get_json(req, timeout)
        return [Plugin.from_dict(d) for d in plugins]

    def get_plugin_option_vals(self, plugin_name, stream_id=None,
                               timeout=DEFAULT_TIMEOUT) \
            -> Dict[str, object]:
        """Gets the current values for every plugin option. See the
        documentation for the PluginOption codec for more info about global and
        stream level options and how they interact.

        :param plugin_name: The plugin to find options for
        :param stream_id: The ID of the stream. If this value is None, then the
            global options are returned for that plugin
        :param timeout: The timeout to use for this request
        :return: A dict where the key is the option name and the value is the
            option's current value
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/options"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/options"
        plugin_option_vals, _ = self._get_json(req, timeout)

        return plugin_option_vals

    def set_plugin_option_vals(self, *, plugin_name, stream_id=None,
                               option_vals: Dict[str, object],
                               timeout=DEFAULT_TIMEOUT):
        """Sets option values for a plugin.

        :param plugin_name: The name of the plugin whose options to set
        :param stream_id: The ID of the stream, if these are stream-level
            options. If this value is None, then the global options are set
        :param option_vals: A dict where the key is the name of the option to
            set, and the value is the value to set that option to
        :param timeout: The timeout to use for this request
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/options"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/options"

        option_values_json = ujson.dumps(option_vals)
        self._put_json(req, timeout, option_values_json)

    def patch_plugin_option_vals(self, *, plugin_name, stream_id=None,
                                 option_vals: Dict[str, object],
                                 timeout=DEFAULT_TIMEOUT):
        """Patches option values for a plugin. Only the provided options are
        changed. To unset an option, provide that option with a value of None.

        :param plugin_name: The name of the plugin whose options to set
        :param stream_id: The ID of the stream, if these are stream-level
            options. If this value is None, then the global options are set
        :param option_vals: A dict where the key is the name of the option to
            set, and the value is the value to set that option to
        :param timeout: The timeout to use for this request
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/options"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/options"

        option_values_json = ujson.dumps(option_vals)
        self._patch_json(req, timeout, option_values_json)

    def is_plugin_active(self, plugin_name, stream_id=None,
                         timeout=DEFAULT_TIMEOUT) -> bool:
        """Returns true if the plugin is active. If a plugin is not marked as
        active, it will not run. Like plugin options, this can be configured
        globally and on a per-stream level.

        :param plugin_name: The name of the plugin to get activity for
        :param stream_id: The ID of the stream, if you want the per-stream
            active setting
        :param timeout: The timeout to use for this request
        :return: True if the plugin is active
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/active"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/active"
        plugins_active, _ = self._get_json(req, timeout)
        return plugins_active

    def set_plugin_active(self, *, plugin_name, stream_id=None,
                          active: Optional[bool],
                          timeout=DEFAULT_TIMEOUT):
        """Sets whether or not the plugin is active. If a plugin is active, it
        will be run on frames.

        :param plugin_name: The name of the plugin to set activity for
        :param stream_id: The ID of the stream, if you want to set the
            per-stream active setting
        :param active: True if the plugin should be set to active
        :param timeout: The timeout to use for this request
        """
        if stream_id is None:
            req = f"/api/plugins/{plugin_name}/active"
        else:
            req = f"/api/streams/{stream_id}/plugins/{plugin_name}/active"

        active_json = ujson.dumps(active)

        self._put_json(req, timeout, active_json)
