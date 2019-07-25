from typing import Tuple
from threading import Thread
from socket import socket
from select import select
from urllib.parse import urlparse

import paramiko

from brainframe.client.api import api
from brainframe.client.api.codecs import StreamConfiguration


class StreamProxy:
    """Proxies local camera streams up to a remote machine where an instance of
    the BrainFrame server is running. This is necessary to give a remote
    BrainFrame server instance access to local cameras that may be behind a
    firewall.
    """

    def __init__(self, server_host,
                 server_port: int,
                 credentials: Tuple[str, str]):
        """
        :param server_host: The host IP/URL of the server to proxy to
        :param server_port: The SSH port to connect to the server on
        :param credentials: The credentials to use while establishing an SSH
            connection to the server
        """
        if credentials is None:
            raise RuntimeError("Stream proxying is not supported without "
                               "credentials")

        self._server_host = server_host
        self._server_port = server_port
        self._credentials = credentials

        self._tunnels = []

        self._client = paramiko.SSHClient()
        # Prints a warning if this is the first time we've connected to the
        # server, instead of causing an error
        self._client.set_missing_host_key_policy(paramiko.WarningPolicy())

        self._client.connect(
            self._server_host,
            self._server_port,
            username=credentials[0],
            password=credentials[1])

    def add(self, stream_configuration: StreamConfiguration):
        """Starts proxying for the given stream configuration.

        :param stream_configuration: The stream to proxy for
        """
        url, port = api.get_proxy_target()

        transport = self._client.get_transport()

        url = stream_configuration.connection_options["url"]
        url = urlparse(url)

        tunnel = self._Tunnel(
            server_port=port,
            camera_host=url.hostname,
            camera_port=url.port,
            transport=transport)
        self._tunnels.append(tunnel)

    def close(self):
        """Stops the proxy."""
        for tunnel in self._tunnels:
            tunnel.close()

        self._client.close()

    class _Tunnel:
        """Tunnels data between the server and a single camera."""

        def __init__(self, server_port: int,
                     camera_host: str,
                     camera_port: int,
                     transport: paramiko.Transport):
            """Starts tunneling data.

            :param server_port: The port on the server to tunnel data to and
                from the camera on
            :param camera_host: The camera's host, an IP or URL
            :param camera_port: The camera's port
            :param transport: A transport to the server
            """
            self._camera_host = camera_host
            self._camera_port = camera_port
            self._transport = transport

            self._running = True
            # All threads that have been spun up to tunnel data
            self._tunnel_threads = []

            transport.request_port_forward("", server_port)

            self._serving_thread = Thread(target=self._serve,
                                          name="ReverseTunnel Serving Thread")
            self._serving_thread.start()

        def close(self):
            """Stops the reverse tunnel."""
            self._running = False

            self._serving_thread.join()
            for thread in self._tunnel_threads:
                thread.join()

        def _serve(self):
            while self._running:
                # Accept incoming connections from the server to the camera
                server_chan = self._transport.accept(100)
                if server_chan is None:
                    continue

                thread = Thread(target=self._tunnel_data, args=(server_chan,),
                                name="ReverseTunnel Connection Thread")
                thread.start()

                self._tunnel_threads.append(thread)

        def _tunnel_data(self, server_chan):
            """Establishes a connection to the camera and tunnels data between
            the camera and the server.

            :param server_chan: The connection to the server
            """

            # Establish a connection to the camera on behalf of the server
            camera_socket = socket()
            camera_socket.connect((self._camera_host, self._camera_port))

            while self._running:
                # Wait for data from either the server or camera
                streams, _, _ = select([server_chan, camera_socket], [], [],
                                       timeout=100)

                # Send camera data to the server, if any is available
                if camera_socket in streams:
                    data = camera_socket.recv(1024)
                    if len(data) != 0:
                        server_chan.send(data)

                # Send server data to the camera, if any is available
                if server_chan in streams:
                    data = server_chan.recv(1024)
                    if len(data) != 0:
                        camera_socket.send(data)
