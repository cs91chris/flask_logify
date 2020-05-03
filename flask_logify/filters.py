import logging


class DisableByPathFilter(logging.Filter):
    def __init__(self, path, name=''):
        """

        :param path:
        :param name:
        """
        self._path = path
        super().__init__(name)

    def filter(self, record):
        """
        add a space or ? after path to ensure subpaths are not excluded from logging

        :param record:
        """
        mess = record.getMessage()
        return not (f"{self._path} " in mess or f"{self._path}?" in mess)
