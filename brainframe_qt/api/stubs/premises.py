from typing import List

from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT
from brainframe.client.api.codecs import Premises


class PremisesStubMixin(BaseStub):
    """Provides stubs for calling APIs to get, set, and delete zones."""

    def get_all_premises(self,
                         timeout=DEFAULT_TIMEOUT) -> List[Premises]:
        """Gets all premises."""
        req = "/api/premises"
        data, _ = self._get_json(req, timeout)
        zones = [Premises.from_dict(j) for j in data]
        return zones

    def get_premises(self, premises_id: int,
                     timeout=DEFAULT_TIMEOUT) -> Premises:
        """Gets the premises with the given ID.

        :param premises_id: The ID of the premises to get
        :param timeout: The timeout to use for this request
        :return: The premises
        """
        req = f"/api/premises/{premises_id}"
        data, _ = self._get_json(req, timeout)

        return Premises.from_dict(data)

    def set_premises(self, premises: Premises,
                     timeout=DEFAULT_TIMEOUT):
        """Update or create a premises. If the Premises doesn't exist, the
        premises.id must be None. An initialized Premises with an ID will be
        returned.
        :param premises: A Premises object
        :param timeout: The timeout to use for this request
        :return: Premises, initialized with an ID
        """

        req = "/api/premises"
        data = self._post_codec(req, timeout, premises)
        new_premises = Premises.from_dict(data)
        return new_premises

    def delete_premises(self, premises_id: int,
                        timeout=DEFAULT_TIMEOUT):
        """Delete a premises and the streams and data connected to it.

        :param premises_id: The ID of the premises to delete
        :param timeout: The timeout to use for this request
        """
        req = f"/api/premises/{premises_id}"
        self._delete(req, timeout)
