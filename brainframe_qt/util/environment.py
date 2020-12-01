import logging
import os


def set_up_environment():
    """Sets up the same environment:

    1) Logging
    2) Tell multiprocessing that it might be running in an executable
    """

    # Set the log level
    default_log_level = "INFO"

    logging.basicConfig(level=os.environ.get("LOGLEVEL", default_log_level))
