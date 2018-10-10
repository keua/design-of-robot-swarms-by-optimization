from enum import IntEnum


class SimpleLogger:

    instance = None

    # @property
    # def instance(self):
    #    """
    #    Returns the singleton for the Logger
    #    :return:
    #    """
    #    if self._instance is None:
    #        SimpleLogger()  # creates and sets a new logger
    #    return self._instance

    class LogLevel(IntEnum):
        DEBUG = 1
        VERBOSE = 2
        INFO = 3
        WARNING = 4
        ERROR = 5

    def __init__(self, level=LogLevel.INFO):
        self.log_level = level

        SimpleLogger.instance = self

    def log_debug(self, message):
        """
        Logs messages with the debug priority. These are the first to be turned off.
        This should log all messages.
        :param message:
        :return:
        """
        if self.log_level <= SimpleLogger.LogLevel.DEBUG:
            print(message)

    def log_verbose(self, message):
        """
        Logs verbosely, more messages than normal but not as detailed as in debug mode
        :param message:
        :return:
        """
        if self.log_level <= SimpleLogger.LogLevel.VERBOSE:
            print(message)

    def log(self, message):
        """
        Logs normally, that is messages that can be needed to trace the flow of the program.
        :param message:
        :return:
        """
        if self.log_level <= SimpleLogger.LogLevel.INFO:
            print(message)

    def log_warning(self, message):
        """
        Logs a warning, the second highest priority level
        :param message:
        :return:
        """
        if self.log_level <= SimpleLogger.LogLevel.WARNING:
            print(message)

    def log_error(self, message):
        """
        Logs an error, the highest priority level
        :param message:
        :return:
        """
        if self.log_level <= SimpleLogger.LogLevel.ERROR:
            print(message)
