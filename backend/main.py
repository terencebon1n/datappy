import logging
import sys

from backend.application.services.api import ApiService
from backend.application.services.consumer import QuixStreamsConsumerService
from backend.application.services.diagram import DiagramService
from backend.application.services.enums import ServiceCommand
from backend.application.services.populate import PopulateService
from backend.application.services.producer import ProducerService
from backend.application.services.registry import ServiceRegistry


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:\t  %(message)s",
    )

    registry = ServiceRegistry()
    registry.register(ServiceCommand.API, lambda: ApiService())
    registry.register(ServiceCommand.POPULATE, lambda: PopulateService())
    registry.register(ServiceCommand.PRODUCER, lambda: ProducerService())
    registry.register(ServiceCommand.CONSUMER, lambda: QuixStreamsConsumerService())
    registry.register(ServiceCommand.DIAGRAM, lambda: DiagramService())

    registry.run(*sys.argv[1:])


if __name__ == "__main__":
    main()
