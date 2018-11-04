"""
``request`` module contains some classes extending another classes from ``requests`` package to make easier requests
to an Airmore server.
"""
import ipaddress

import requests.exceptions


class AirmoreRequest(requests.PreparedRequest):
    # todo 1 - class doc

    def __init__(self, session: "AirmoreSession"):
        super().__init__()
        self.__session = session  # type: AirmoreSession
        self.prepare_method(None)

    def prepare_method(self, method):
        # todo 2 - method doc

        self.method = "POST"

    def prepare_url(self, url, params):
        # todo 2 - method doc

        super().prepare_url(self.__session.base_url+url, params)


class ApplicationOpenRequest(AirmoreRequest):
    # todo 1 - class doc

    def __init__(self, session: "AirmoreSession"):
        super().__init__(session)
        self.prepare_url("/", {"Key": "PhoneCheckAuthorization"})


class AuthorizationRequest(AirmoreRequest):
    # todo 1 - class doc

    def __init__(self, session: "AirmoreSession"):
        super().__init__(session)
        self.prepare_url("/", {"Key": "PhoneRequestAuthorization"})


class AirmoreSession(requests.Session):
    """``AirmoreSession`` extends ``requests.Session`` in order to manage an Airmore session."""

    def __init__(self, ip_address: ipaddress.IPv4Address, port: int = 2333):
        """
        :param ip_address: IP address to connect to.
        :param port: Port to connect to.
        """
        super().__init__()

        self.ip_address = ip_address  # type: ipaddress.IPv4Address
        self.port = port  # type: int

    @property
    def is_server_running(self) -> bool:
        """Whether the Airmore server runs or not.

        The server is connected via a socket connection.

        :return: True if the server runs.
        """

        import socket
        from contextlib import closing

        is_running = False
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((str(self.ip_address), self.port)) == 0:
                is_running = True

        return is_running

    @property
    def is_application_open(self) -> bool:
        """Whether the application is open and front.

        This means the user now can see Airmore application on screen.

        :return: True if the application is open and front.
        """
        # now i know what you are thinking
        # i don't know what these devs were thinking
        # but, apparently, the url below checks if the application
        # is open and user can see it

        request = ApplicationOpenRequest(self)
        response = self.send(request)
        status = response.status_code
        body = response.text

        if status != 200:
            return False

        is_app_front = False

        if body == '"0"':
            is_app_front = True

        return is_app_front

    def request_authorization(self) -> bool:
        """Requests authorization from the device.

        This method will block the thread until the authorization accepted on the device. You might
        want to utilize async if you do not want to hang your application.

        The authorization on device will be rejected automatically after 30 seconds.

        Running this method before each request is a good practice since the target device will not show authorization
        dialog if the session is already authorized.

        :return: True if the authorization was accepted.
        """

        request = AuthorizationRequest(self)
        response = self.send(request)

        is_accepted = False

        if response.text == "true":
            is_accepted = True

        return is_accepted

    def request(self, method, url, params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None,
                json=None) -> requests.Response:
        # todo 2 - method doc

        self.request_authorization()

        new_url = self.base_url + url

        return super().request(method, new_url, params, data, headers, cookies, files, auth, timeout, allow_redirects,
                               proxies, hooks, stream, verify, cert, json)

    def send(self, request, **kwargs):
        return super().send(request, **kwargs)

    @property
    def base_url(self) -> str:
        """Constructs a base url (prefix) for any AirmoreRequest.

        :return: A base url for internal requests.
        """

        prefix = "http"

        return "{}://{}:{}".format(prefix, self.ip_address, self.port)


__all__ = [
    "AirmoreSession",
    "AirmoreRequest"
]


class ServerUnreachableException(Exception):
    """
    This exception is thrown when:
     - No Airmore server was found on target session.
     - Airmore server is idle on target session.
    """

    def __init__(self, service):
        message = "Server is found idle while making request for {}. The reasons might be:\n" \
                  " - You might not even have installed Airmore to your device.\n" \
                  " - Sometimes your Airmore server goes idle for battery saving. You need to open it up again." \
            .format(service.__class__.__name__)
        super().__init__(message)


class AuthorizationException(Exception):
    """
    This exception is thrown when the authorization is rejected by the device.
    """

    def __init__(self):
        message = "You are not authorized for this session. Please accept authorization on target device."
        super().__init__(message)
