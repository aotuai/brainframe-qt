import logging

from brainframe.client.api.stubs.stub import Stub
from brainframe.client.api.codecs import EngineConfiguration


class EngineConfigurationStubMixin(Stub):
    """Provides stubs for calling APIs that access the engine configuration.

    If you're here to delete this and engine configurations in general, hit me
    up and we'll party down.
    """

    def get_engine_configuration(self) -> EngineConfiguration:
        """Returns the capabilities of the machine learning engine on the
        server.

        Currently, it can tell you:
            The types of objects that can be detected
            The types of attributes that can be detected for each object.

        :return: EngineConfiguration
        """
        logging.warning("Deprecated: Engine configurations will be removed in "
                        "a future release")
        req = "/api/engine-configuration"
        resp = self._get(req)
        return EngineConfiguration.from_dict(resp)
