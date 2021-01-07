import logging

import flask


class RequestFormatter(logging.Formatter):
    def format(self, record):
        na = 'NA'
        record.url = na
        record.path = na
        record.method = na
        record.scheme = na
        record.remote_addr = na
        record.request_id = na

        if flask.has_request_context():
            record.url = flask.request.url
            record.method = flask.request.method
            record.scheme = flask.request.scheme
            record.path = flask.request.full_path
            record.remote_addr = flask.request.remote_addr

            h = flask.current_app.config.get('REQUEST_ID_HEADER') or 'X-Request-ID'
            header = "HTTP_{}".format(h.upper().replace('-', '_'))
            req_id = flask.g.request_id or flask.request.environ.get(header)
            if req_id:
                record.request_id = req_id

        return super().format(record)
