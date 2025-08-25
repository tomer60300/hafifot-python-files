from config import parse_args
import logging
from logging_conf import configure_logging
from operation.search import walk_filesystem_by_filters, archive_files_by_filters

if __name__ == "__main__":
    configure_logging("DEBUG")
    logger = logging.getLogger(__name__)

    try:
        config = parse_args()
        logger.info("Parsed config: %s", config)
        logger.debug(
            "Special mode %s" % ("*Size* " if config.size != 0 else "") + ("*Archive* " if config.archive_name else ""))

        if config.archive_name:
            archive_files_by_filters(config.archive_name,config.folder, config.depth, config.pattern, config.size)  # Todo call params missing
        else:
            for result in walk_filesystem_by_filters(config.folder, config.depth, config.pattern, config.size):
                print(f"{result} -- ", end="")
    except Exception as ex:
        logger.critical("Fatal error: %s", ex, exc_info=True)
        raise
    except SystemExit as ex:
        logger.critical("Argument parsing failed. Exit code=%s", ex.code)
