from flask import request


class LogBuilder:
    def __init__(self, get_remote=lambda: None):
        """

        :param get_remote:
        """
        self._get_remote = get_remote

    def dump_request(self):
        """

        """
        raise NotImplementedError

    def dump_response(self, response):
        """

        :param response: Response object
        :return:
        """
        raise NotImplementedError

    def get_remote_address(self):
        """

        :return: client ip address
        """
        return self._get_remote() or request.remote_addr
