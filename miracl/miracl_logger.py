import logging
import sys


class InfoFilter(logging.Filter):
    """
    A custom logging filter that dynamically changes the formatter based on the log level.

    This filter switches between info and debug formatters for a given stream handler
    based on the log record's level.

    :param stream_handler: The stream handler to modify
    :type stream_handler: logging.StreamHandler
    :param info_formatter: The formatter to use for INFO level messages
    :type info_formatter: logging.Formatter
    :param debug_formatter: The formatter to use for DEBUG level messages
    :type debug_formatter: logging.Formatter
    """

    def __init__(self, stream_handler, info_formatter, debug_formatter):
        super().__init__()
        self.stream_handler = stream_handler
        self.info_formatter = info_formatter
        self.debug_formatter = debug_formatter

    def filter(self, record):
        """
        Apply the appropriate formatter based on the log record's level.

        :param record: The log record to filter
        :type record: logging.LogRecord
        :return: Always returns True to allow the record to be processed
        :rtype: bool
        """
        if record.levelno == logging.INFO:
            self.stream_handler.setFormatter(self.info_formatter)
        else:
            self.stream_handler.setFormatter(self.debug_formatter)
        return True


def setup_logger(log_to_file=True):
    """
    Set up and configure a logger with customized formatting for debug and info levels.

    This function creates a logger that can output to both console and file (optional).
    It uses different formatters for debug and info level messages.

    :param log_to_file: Boolean flag to enable or disable logging to a file
    :type log_to_file: bool
    :return: Configured logger object
    :rtype: logging.Logger

    :Example:

    >>> logger = setup_logger(log_to_file=True)
    >>> logger.debug("Debug message")
    >>> logger.info("Info message")

    .. note::
       When `log_to_file` is True, debug messages are logged to 'debug.log'.

    .. warning::
       Ensure write permissions in the current directory when `log_to_file` is True.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    debug_formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    )
    info_formatter = logging.Formatter("INFO: %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(debug_formatter)
    logger.addHandler(stream_handler)

    if log_to_file:
        file_handler = logging.FileHandler("debug.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(debug_formatter)
        logger.addHandler(file_handler)

    info_filter = InfoFilter(stream_handler, info_formatter, debug_formatter)
    logger.addFilter(info_filter)

    return logger


logger = setup_logger(log_to_file=False)  # Set to False to disable file logging
