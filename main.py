from schema.parser import parse_args
import logging
from logging_conf import configure_logging
from operations.operation import execute

if __name__ == "__main__":
    configure_logging("DEBUG")
    logger = logging.getLogger(__name__)

    try:
        config = parse_args()
        logger.info("Parsed schema: %s", config)
        logger.debug(
            "Special mode %s" % ("*Size* " if config.max_size is not None else "") + ("*Archive* " if config.archive_name else ""))

        execute(config)

    except Exception as ex:
        logger.critical("Fatal error: %s", ex, exc_info=True)
        raise
    except SystemExit as ex:
        logger.critical("Argument parsing failed. Exit code=%s", ex.code)
