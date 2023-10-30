import logging


from enum import Enum


class ANSIColor(Enum):
    RESET = "\x1b[0m"
    GREY = "\x1b[38;20m"
    LIGHT_BLUE = "\x1b[34;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"


def create_text(color: ANSIColor):
    """
    Create a text with color
    """
    return f"[%(asctime)s]-[{color}%(levelname)s{ANSIColor.RESET.value}]: %(message)s"


class CustomFormatter(logging.Formatter):
    """
    Custom formatter to add colors to logging
    """

    FORMATS = {
        logging.DEBUG: create_text(ANSIColor.GREY.value),
        logging.INFO: create_text(ANSIColor.LIGHT_BLUE.value),
        logging.WARNING: create_text(ANSIColor.YELLOW.value),
        logging.ERROR: create_text(ANSIColor.RED.value),
        logging.CRITICAL: create_text(ANSIColor.BOLD_RED.value),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)
