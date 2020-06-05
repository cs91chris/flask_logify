import json
import logging.config
import sys
from json import JSONDecodeError

import yaml
from flask import current_app as cap, request
from yaml.parser import ParserError
from yaml.scanner import ScannerError


class FlaskLogging:
    def __init__(self, app=None, **kwargs):
        """

        :param app:
        """
        self._conf = {}

        if app is not None:
            self.init_app(app, **kwargs)

    @property
    def conf(self):
        """

        :return:
        """
        return self._conf

    def init_app(self, app, **kwargs):
        """

        :param app: Flask app instance
        :param kwargs: extra logging configuration
        """
        if not hasattr(app, 'extensions'):
            app.extensions = dict()
        app.extensions['logify'] = self

        self.set_default_config(app)

        if not app.config['LOG_DISABLE_HOOKS']:
            app.before_request_funcs.setdefault(None, []).append(self.log_request)
            app.after_request_funcs.setdefault(None, []).append(self.log_response)

        if 'LOG_FILE_CONF' in app.config:
            try:
                self.conf_from_file(app.config['LOG_FILE_CONF'])
            except OSError as exc:
                app.logger.exception(exc, stack_info=False)

            try:
                self._conf.update(kwargs)
                logging.config.dictConfig(self._conf)
                app.logger = logging.getLogger(app.config['LOG_LOGGER_NAME'])
            except ValueError as exc:
                app.logger.error('bad configuration file: {}'.format(app.config['LOG_FILE_CONF']))
                app.logger.error('the configuration below\n{}'.format(self._conf))
                app.logger.exception(exc, stack_info=False)
        else:
            app.logger.warning("No 'LOG_FILE_CONF' provided using default configuration")

        if app.config.get('DEBUG') is True:
            app.logger.setLevel('DEBUG')
            self.set_werkzeug_handlers(app.logger.handlers)

    def conf_from_file(self, filename):
        """

        :param filename:
        """
        with open(filename) as f:
            try:
                self._conf = yaml.safe_load(f)
            except (ParserError, ScannerError) as yex:
                try:
                    self._conf = json.load(f)
                except (TypeError, JSONDecodeError) as jex:
                    print(yex, file=sys.stderr)
                    print(jex, file=sys.stderr)
                    sys.exit(1)

    def log_request(self):
        """

        """
        body = None
        headers = None
        skip = cap.config['LOG_SKIP_DUMP']
        hdr = cap.config['LOG_REQ_HEADERS']

        if '{headers}' in cap.config['LOG_RESP_FORMAT'] and not skip:
            headers = self.dump_headers(request.headers, hdr)

        if '{body}' in cap.config['LOG_RESP_FORMAT'] and not skip:
            body = self.dump_body(request)

        request_dumped = cap.config['LOG_REQ_FORMAT'].format(
            address=self.get_remote_address(),
            method=request.method,
            scheme=request.scheme,
            path=request.full_path,
            headers=headers,
            body=body
        )

        cap.logger.info("INCOMING REQUEST: {}".format(request_dumped))

    def log_response(self, response):
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

        if '{headers}' in cap.config['LOG_RESP_FORMAT'] and not skip:
            headers = self.dump_headers(response.headers, hdr)

        if '{body}' in cap.config['LOG_RESP_FORMAT'] and not skip:
            body = self.dump_body(response)

        response_dumped = cap.config['LOG_RESP_FORMAT'].format(
            level=level,
            status=response.status,
            headers=headers,
            body=body
        )

        cap.logger.debug("OUTGOING RESPONSE at {} {}".format(request.path, response_dumped))
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

    @staticmethod
    def set_default_config(app):
        """

        param app: Flask app instance
        """
        app.config.setdefault('LOG_REQ_HEADERS', [])
        app.config.setdefault('LOG_RESP_HEADERS', [])
        app.config.setdefault('LOG_DISABLE_HOOKS', False)
        app.config.setdefault('LOG_SKIP_DUMP', not app.config.get('DEBUG'))
        app.config.setdefault('LOG_RESP_FORMAT', "{level} STATUS {status}\n{headers}\n\n{body}\n")
        app.config.setdefault('LOG_REQ_FORMAT', "{address} {method} {scheme} {path}\n{headers}\n\n{body}\n")
        app.config.setdefault('LOG_APP_NAME', 'flask')
        app.config.setdefault('LOG_LOGGER_NAME', '{}-{}'.format(
            app.config['LOG_APP_NAME'],
            app.config.get('FLASK_ENV') or 'development'
        ))

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

    @staticmethod
    def set_werkzeug_handlers(handlers):
        """

        :param handlers:
        """
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.DEBUG)
        for hdl in handlers:
            werkzeug_logger.addHandler(hdl)
