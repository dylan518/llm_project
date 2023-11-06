'''
# logger_config.py
import logging
from logging.handlers import RotatingFileHandler

# Define custom log level for AI readability
AI_READABLE = 25
logging.addLevelName(AI_READABLE, "AI_READABLE")


class CustomLogger(logging.Logger):

    def ai_readable(self, msg, *args, **kwargs):
        self.log(AI_READABLE, msg, *args, **kwargs)


logging.setLoggerClass(CustomLogger)


def configure_logger(log_level=logging.INFO):
    logger = logging.getLogger('SelfImprovementLogger')
    logger.setLevel(log_level)

    # Create a file handler with a rotating mechanism
    fh = RotatingFileHandler('self_improvement.log',
                             maxBytes=100000,
                             backupCount=5)
    fh.setLevel(log_level)

    # Create a console handler for lower level debug messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create formatters and add them to the handlers
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    fh.setFormatter(file_formatter)
    ch.setFormatter(console_formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def get_logger():
    return logging.getLogger('SelfImprovementLogger')


# Usage:
# logger = get_logger()
# logger.ai_readable('This message is readable by the AI.')
# logger.info('This is an info message.')
'''