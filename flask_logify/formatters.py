import logging
import sys


class RequestFormatter(logging.Formatter):
    def format(self, record):
        """

        :param record:
        :return:
        """
        try:
            # noinspection PyUnresolvedReferences
            request = record.request_context

            record.url = request.url
            record.method = request.method
            record.scheme = request.scheme
            record.path = request.full_path
            record.remote_addr = request.remote_addr
            record.request_id = request.environ.get("HTTP_X_REQUEST_ID")
        except AttributeError as exc:
            print(self, '-', str(exc), file=sys.stderr)

        return super().format(record)
