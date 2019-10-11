from brainframe.client.api.stubs.base_stub import BaseStub, DEFAULT_TIMEOUT


class AnalysisStubMixin(BaseStub):
    """Provides stubs for calling APIs that control analysis on streams."""

    def start_analyzing(self, stream_id,
                        timeout=DEFAULT_TIMEOUT) -> bool:
        """Starts analysis on this stream.

        :param stream_id: The ID of the stream to start analysis on
        :param timeout: The timeout to use for this request
        :return: True or False if the server was able to start analysis on that
            stream. It could fail because: unable to start stream, or license
            restrictions.
        """
        req = f"/api/streams/{stream_id}/analyze"
        resp = self._put_json(req, timeout, 'true')
        return resp

    def stop_analyzing(self, stream_id,
                       timeout=DEFAULT_TIMEOUT):
        """Stops analysis on this stream.

        :param stream_id: The ID of the stream to stop analysis on
        :param timeout: The timeout to use for this request
        :return: True or False if the server was able to start analysis on that
            stream. It could fail because: unable to start stream, or license
            restrictions.
        """
        req = f"/api/streams/{stream_id}/analyze"
        resp = self._put_json(req, timeout, 'false')
        return resp
