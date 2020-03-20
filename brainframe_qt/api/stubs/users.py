from typing import List

from .base_stub import BaseStub, DEFAULT_TIMEOUT
from brainframe.client.api.codecs import User


class UserStubMixin(BaseStub):
    """Provides stubs for calling APIs related to user management."""

    def get_user(self, user_id,
                 timeout=DEFAULT_TIMEOUT) -> User:
        """Gets the user with the given ID.

        :param user_id: The ID of the user to get
        :param timeout: The timeout to use for this request
        :return: The user
        """
        req = f"/api/users/{user_id}"
        data, _ = self._get_json(req, timeout)

        return User.from_dict(data)

    def get_users(self, timeout=DEFAULT_TIMEOUT) -> List[User]:
        """Gets all users.

        :param timeout: The timeout to use for this request
        :return: Users
        """
        req = f"/api/users"
        data, _ = self._get_json(req, timeout)

        return [User.from_dict(u) for u in data]

    def set_user(self, user, timeout=DEFAULT_TIMEOUT) -> User:
        """Creates or updates a user. Only admin users may make this request.

        A new user is created if the given user's ID is None.

        :param user: The user to create or update
        :param timeout: The timeout to use for this request
        :return: Created or updated user
        """
        req = f"/api/users"
        data = self._post_codec(req, timeout, user)

        return User.from_dict(data)

    def delete_user(self, user_id, timeout=DEFAULT_TIMEOUT):
        """Deletes a user. Only admin users may make this request.

        :param user_id: The ID of the user to delete
        :param timeout: The timeout to use for this request
        """
        req = f"/api/users/{user_id}"
        self._delete(req, timeout)
