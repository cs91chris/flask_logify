import logging

import flask


class RequestIDFormatter(logging.Formatter):
    def format(self, record):
        record.request_id = 'NA'

        if flask.has_request_context():
            h = flask.current_app.config.get('REQUEST_ID_HEADER') or 'X-Request-ID'
            header = "HTTP_{}".format(h.upper().replace('-', '_'))
            req_id = flask.request.environ.get(header)
            if req_id:
                record.request_id = req_id

        return super().format(record)
