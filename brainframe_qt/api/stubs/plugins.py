from typing import Dict, List, Optional

import ujson

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import PluginOption


class PluginStubMixin(Stub):
    """Provides stubs to call APIs to inspect and configure plugins."""

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

    def set_plugin_active(self, *, plugin_name, stream_id=None,
                          active: Optional[bool]):
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
