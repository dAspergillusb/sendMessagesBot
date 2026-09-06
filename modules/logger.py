import logging
from os import makedirs
from sys import stdout


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_logger(**kwargs)
        return cls._instance

    @staticmethod
    def _setup_logger(**kwargs) -> None:
        makedirs("./logs", exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        log_format = logging.Formatter("%(asctime)s - [%(levelname)s] - %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        if kwargs.get("to_file", True):
            file_handler = logging.FileHandler(filename="./logs/main_log", encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(log_format)
            logger.addHandler(file_handler)

        if kwargs.get("to_stdout", False):
            stream_handler = logging.StreamHandler(stdout)
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(log_format)
            logger.addHandler(stream_handler)


