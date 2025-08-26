from config import parse_args
import logging
from logging_conf import configure_logging
from directory.search import walk_with_depth

if __name__ == "__main__":
    configure_logging("DEBUG")
    logger = logging.getLogger(__name__)

    try:
        config = parse_args()
        logger.info("Parsed config: %s", config)

        for result in walk_with_depth(config.folder, config.depth,config.pattern):
            print(f"{result} -- ",end="")
    except Exception as ex:
        logger.critical("Fatal error: %s", ex, exc_info=True)
        raise
    except SystemExit as ex:
        logger.critical("Argument parsing failed. Exit code=%s", ex.code)
