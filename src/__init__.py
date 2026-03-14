import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(message)s",
)

logger = logging.getLogger(__name__)
