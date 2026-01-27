import logging


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - %(name)-26s - %(levelname)-7s - %(message)s",
    )
