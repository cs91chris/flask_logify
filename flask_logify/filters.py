import logging


class DisableByPathFilter(logging.Filter):
    def __init__(self, path, name=''):
        """

        :param path:
        :param name:
        """
        super().__init__(name)

        # add a space or ? after path
        # to ensure sub-paths are not accidentally excluded from logging
        self._excluded = (
            "{} ".format(path),
            "{}?".format(path),
        )

    def filter(self, record):
        """

        :param record:
        :return: False if message must be filtered
        """
        for i in self._excluded:
            if i in record.getMessage():
                return False

        return True
