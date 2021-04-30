from abc import ABC

import flask
from flask import current_app as cap

from .base import BaseWrapper, LogBuilder


class Wrapper(BaseWrapper, ABC):
    @staticmethod
    def padding(text):
        return f"\n{text}"

    def dump_headers(self, hdr, only=()):
        """
        dumps http headers

        :param hdr: headers' dictionary
        :param only: list of headers key to dump
        :return: string representation of headers
                k1: v1
                k2: v2
        """
        if only:
            hdr = {k: hdr[k] for k in only if k in hdr}

        return self.padding('\n'.join(f'{k}: {v}' for k, v in hdr.items()))

    def dump_body(self, r):
        """
        dump http body as plain text

        :param r: Response object
        :return:
        """
        try:
            return self.padding(r.get_data(as_text=True))
        except UnicodeError:
            return 'body not dumped: invalid encoding or binary file'


class RequestWrap(Wrapper):
    def dump(self):
        body = headers = ''
        request = self.data
        fmt = self.opts.get('fmt')
        hdr = self.opts.get('only')
        skip = self.opts.get('skip')
        address = self.opts.get('addr')

        if '{headers}' in fmt and (hdr or not skip):
            headers = self.dump_headers(request.headers, hdr)
        if '{body}' in fmt and not skip:
            body = self.dump_body(request)

        return fmt.format(
            address=address,
            method=request.method,
            scheme=request.scheme,
            path=request.full_path,
            headers=headers,
            body=body
        )


class ResponseWrap(Wrapper):
    def dump(self):
        body = headers = ''
        response = self.data
        fmt = self.opts.get('fmt')
        hdr = self.opts.get('only')
        skip = self.opts.get('skip')
        level = self.opts.get('level')

        if '{headers}' in fmt and (hdr or not skip):
            headers = self.dump_headers(response.headers, hdr)
        if '{body}' in fmt and not skip:
            body = self.dump_body(response)

        dump_resp = fmt.format(
            level=level,
            status=response.status,
            headers=headers,
            body=body
        )
        return f"{flask.request.path} {dump_resp}"


class LogTextBuilder(LogBuilder):
    wrapper_dump_request = RequestWrap
    wrapper_dump_response = ResponseWrap

    def request_params(self):
        return {
            'addr': self.get_remote_address(),
            'skip': cap.config['LOG_REQ_SKIP_DUMP'],
            'only': cap.config['LOG_REQ_HEADERS'],
            'fmt':  cap.config['LOG_REQ_FORMAT'],
        }

    def response_params(self):
        return {
            'skip': cap.config['LOG_RESP_SKIP_DUMP'],
            'only': cap.config['LOG_RESP_HEADERS'],
            'fmt':  cap.config['LOG_RESP_FORMAT'],
        }
