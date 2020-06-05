from datetime import datetime

from flask import current_app as cap, json, request

from .base import LogBuilder


class LogJSONBuilder(LogBuilder):
    @staticmethod
    def package_message(identifier, payload):
        """

        :param identifier:
        :param payload:
        :return:
        """
        return json.dumps({
            'appName': cap.config['LOG_APP_NAME'],
            'serverName': cap.config['SERVER_NAME'],
            'timestamp': datetime.utcnow().timestamp(),
            'type': identifier,
            **payload,
        })

    def dump_request(self):
        """

        """
        body = None
        headers = None
        skip = cap.config['LOG_SKIP_DUMP']
        hdr = cap.config['LOG_REQ_HEADERS']

        if hdr or not skip:
            headers = self.dump_headers(request.headers, hdr)

        if not skip:
            body = self.dump_body(request)

        request_dumped = dict(
            address=self.get_remote_address(),
            method=request.method,
            scheme=request.scheme,
            path=request.full_path,
            headers=headers,
            body=body
        )

        cap.logger.info(self.package_message('request', request_dumped))

    def dump_response(self, response):
        """

        :param response: Response object
        """
        body = None
        headers = None
        skip = cap.config['LOG_SKIP_DUMP']
        hdr = cap.config['LOG_REQ_HEADERS']

        if hdr or not skip:
            headers = self.dump_headers(response.headers, hdr)

        if not skip:
            body = self.dump_body(response)

        cap.logger.info(self.package_message('response', dict(
            path=request.path,
            status=response.status,
            headers=headers,
            body=body
        )))

        return response

    @staticmethod
    def dump_headers(hdr, only=()):
        """
        dumps http headers

        :param hdr: headers' dictionary
        :param only: list of headers key to dump
        :return: string representation of headers
                k1: v1
                k2: v2
        """
        def dump(h):
            return {k: v for k, v in h.items()}

        if only:
            return dump({k: hdr[k] for k in only if k in hdr})

        return dump(hdr)

    @staticmethod
    def dump_body(r):
        """

        :param r:
        :return:
        """
        body = r.get_json()
        if body:
            return body

        try:
            return r.get_data(as_text=True)
        except UnicodeError:
            return 'body not dumped: invalid encoding or binary'
