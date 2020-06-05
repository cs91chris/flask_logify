from flask import request


class LogBuilder:
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

    @staticmethod
    def get_remote_address():
        """

        :return: client ip address
        """
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            request.environ['REMOTE_ADDR'] = request.environ['HTTP_X_FORWARDED_FOR']
        elif request.environ.get('HTTP_X_REAL_IP'):
            request.environ['REMOTE_ADDR'] = request.environ['HTTP_X_REAL_IP']

        return request.environ['REMOTE_ADDR']
