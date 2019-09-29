import logging
import logging.handlers
import os


def init_logger(log):

    # set default log root folder and debug level
    log_root = "./" if "HOME" not in os.environ else f"{os.environ['HOME']}/"
    log.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] %(message)s"
    )

    # set handler output warnings and errors to file and revolve if size exceed 1GB
    log_path = log_root + ".minjob.log"
    fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=pow(2, 30))
    fh.setFormatter(fmt=formatter)
    fh.setLevel(logging.INFO)
    log.addHandler(fh)

    # set handler output debug to errors to stdout
    ch = logging.StreamHandler()
    ch.setFormatter(fmt=formatter)
    ch.setLevel(logging.ERROR)
    log.addHandler(ch)

    return log


# TODO: allow the user to change the log root folder
logger = init_logger(logging.getLogger("minjob"))
