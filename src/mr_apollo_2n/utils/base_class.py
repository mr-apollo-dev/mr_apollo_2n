import logging
from typing import Optional


class BaseClass:
    """
    Base class with a logger attribute.

    This class provides a logger attribute that can be used for logging in derived classes.

    Attributes:
            logger (logging.Logger): The logger object for logging.
    """

    def __init__(
        self,
        logger_name: Optional[str] = None,
        log_level: Optional[int] = logging.DEBUG,
    ):
        """
        Initializes the BaseClassWithLogger.

        Parameters:
        -----------
        logger_name (str, optional):
                The name of the logger (default is None).
        log_level (int, optional):
                The logging level of the logger (default is logging.DEBUG).

        """
        # Configure the logger with the provided name or the class name
        self.logger = logging.getLogger(logger_name or self.__class__.__name__)
        self.logger.setLevel(log_level if log_level is not None else logging.DEBUG)

        # Configure a console handler to view logs in the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(
            logging.DEBUG
        )  # Set the console handler's logging level to DEBUG

        # Define a log format for the logs
        log_format = logging.Formatter(
            "%(asctime)s [%(levelname)-5s] [%(name)-25s] - %(message)s"
        )
        console_handler.setFormatter(log_format)

        # Add the console handler to the logger
        self.logger.addHandler(console_handler)
