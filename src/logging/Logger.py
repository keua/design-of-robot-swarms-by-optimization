from enum import IntEnum


class Logger:

    instance = None

    class LogLevel(IntEnum):
        DEBUG = 1
        VERBOSE = 2
        INFO = 3
        WARNING = 4
        ERROR = 5

    def __init__(self, level=LogLevel.INFO):
        self.log_level = level

        Logger.instance = self

    def log_debug(self, message):
        """
        Logs messages with the debug priority. These are the first to be turned off.
        This should log all messages.
        :param message:
        :return:
        """
        if self.log_level <= Logger.LogLevel.DEBUG:
            print(message)

    def log_verbose(self, message):
        """
        Logs verbosely, more messages than normal but not as detailed as in debug mode
        :param message:
        :return:
        """

    def log(self, message):
        """
        Logs normally, that is messages that can be needed to trace the flow of the program.
        :param message:
        :return:
        """
        if self.log_level <= Logger.LogLevel.INFO:
            print(message)

    def log_warning(self, message):
        """
        Logs a warning, the second highest priority level
        :param message:
        :return:
        """
        if self.log_level <= Logger.LogLevel.WARNING:
            print(message)

    def log_error(self, message):
        """
        Logs an error, the highest priority level
        :param message:
        :return:
        """
        if self.log_level <= Logger.LogLevel.ERROR:
            print(message)
