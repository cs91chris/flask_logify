from flask import current_app as cap, request

from .base import LogBuilder


class LogTextBuilder(LogBuilder):
    def dump_request(self):
        """

        """
        body = None
        headers = None
        skip = cap.config['LOG_SKIP_DUMP']
        hdr = cap.config['LOG_REQ_HEADERS']

        if '{headers}' in cap.config['LOG_RESP_FORMAT'] and (hdr or not skip):
            headers = self.dump_headers(request.headers, hdr)

        if '{body}' in cap.config['LOG_RESP_FORMAT'] and not skip:
            body = self.dump_body(request)

        cap.logger.info("INCOMING REQUEST: {}".format(cap.config['LOG_REQ_FORMAT'].format(
            address=self.get_remote_address(),
            method=request.method,
            scheme=request.scheme,
            path=request.full_path,
            headers=headers,
            body=body
        )))

    def dump_response(self, response):
        """

        :param response: Response object
        """
        code = int(response.status_code / 100)
        if code in (1, 2, 3):
            level = 'SUCCESS'
        elif code == 4:
            level = 'WARNING'
        elif code == 5:
            level = 'ERROR'
        else:
            level = 'UNKNOWN'

        body = None
        headers = None
        skip = cap.config['LOG_SKIP_DUMP']
        hdr = cap.config['LOG_REQ_HEADERS']

        if '{headers}' in cap.config['LOG_RESP_FORMAT'] and (hdr or not skip):
            headers = self.dump_headers(response.headers, hdr)

        if '{body}' in cap.config['LOG_RESP_FORMAT'] and not skip:
            body = self.dump_body(response)

        cap.logger.debug(
            "OUTGOING RESPONSE at {} {}".format(request.path, cap.config['LOG_RESP_FORMAT'].format(
                level=level,
                status=response.status,
                headers=headers,
                body=body
            ))
        )
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
            return '\n'.join('{}: {}'.format(k, v) for k, v in h.items())

        if only:
            return dump({k: hdr[k] for k in only if k in hdr})

        return dump(hdr)

    @staticmethod
    def dump_body(r):
        """
        dump http body as plain text

        :param r: Response object
        :return:
        """
        try:
            return r.get_data(as_text=True) or 'empty data'
        except UnicodeError:
            return 'body not dumped: invalid encoding or binary'
