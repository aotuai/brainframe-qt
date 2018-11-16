from brainframe.client.api.stubs.stub import Stub


class AnalysisStubMixin(Stub):
    """Provides stubs for calling APIs that control analysis on streams."""

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
