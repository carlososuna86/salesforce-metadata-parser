import json
import logging.config
import os
import time

default_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simpleFormatter": {
            "format": "%(levelname)-5s|%(message)s",
        },
        "detailedFormatter": {
            "format": "%(asctime)s|%(levelname)-5s|%(filename)s:%(lineno)d|%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "formatter": "simpleFormatter",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "fileHandler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailedFormatter",
            "level": "DEBUG",
            "filename": "logs/salesforce-metadata-parser.log",
            "when": "M",
            "interval": 1,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": [
                "consoleHandler",
                "fileHandler"
            ]
        }
    }
}

def _load_config(file_name: str):
    if os.path.isfile(file_name):
        with open(file_name, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        return config

    return default_config


def _namer():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
    log_file = f"salesforce-metadata-parser_{timestamp}.log"

    return os.path.join(log_dir, log_file)


def configure_root_logger():
    log_path = _namer()

    # Load Logging configuration
    config = _load_config("logging.json")

    # Replace the Filename
    for handler in config.get("handlers", {}).values():
        if "filename" in handler.keys():
            handler["filename"] = log_path

    # Create the Root logger from the configuration
    logging.config.dictConfig(config)
