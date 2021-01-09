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

            if hasattr(flask.g, 'request_id'):
                request_id = flask.g.request_id
            else:
                h = flask.current_app.config['REQUEST_ID_HEADER']
                header = "HTTP_{}".format(h.upper().replace('-', '_'))
                request_id = flask.request.environ.get(header)

            if request_id:
                record.request_id = request_id

        return super().format(record)
