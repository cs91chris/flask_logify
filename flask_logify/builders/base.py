from abc import ABC, abstractmethod
from flask import request, current_app as cap


class BaseWrapper(ABC):
    def __init__(self, data, **opts):
        self.data = data
        self.opts = opts

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.dump()

    @abstractmethod
    def dump(self):
        """"""


class LogBuilder:
    wrapper_dump_request = BaseWrapper
    wrapper_dump_response = BaseWrapper

    def __init__(self, get_remote=lambda: None):
        """

        :param get_remote:
        """
        self._get_remote = get_remote

    @abstractmethod
    def request_params(self):
        """"""

    @abstractmethod
    def response_params(self):
        """"""

    def get_remote_address(self):
        """

        :return: client ip address
        """
        return self._get_remote() or request.remote_addr

    @staticmethod
    def level_from_code(code):
        code = int(code / 100)
        if code in (1, 2, 3):
            return cap.logger.info, 'SUCCESS'
        elif code == 4:
            return cap.logger.warning, 'WARNING'
        elif code == 5:
            return cap.logger.warning, 'ERROR'
        else:
            return cap.logger.warning, 'ERROR'

    def dump_request(self):
        cap.logger.info("%s", self.wrapper_dump_request(
            request, **self.request_params()
        ))

    def dump_response(self, response):
        log, level = self.level_from_code(response.status_code)
        log("%s", self.wrapper_dump_response(
            response, level=level, **self.response_params()
        ))
        return response
