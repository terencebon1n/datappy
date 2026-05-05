import sys

from src.application.services.api import ApiService
from src.application.services.consumer import QuixStreamsConsumerService
from src.application.services.diagram import DiagramService
from src.application.services.enums import ServiceCommand
from src.application.services.populate import PopulateService
from src.application.services.producer import ProducerService
from src.application.services.registry import ServiceRegistry


def main() -> None:
    registry = ServiceRegistry()
    registry.register(ServiceCommand.API, lambda: ApiService())
    registry.register(ServiceCommand.POPULATE, lambda: PopulateService())
    registry.register(ServiceCommand.PRODUCER, lambda: ProducerService())
    registry.register(ServiceCommand.CONSUMER, lambda: QuixStreamsConsumerService())
    registry.register(ServiceCommand.DIAGRAM, lambda: DiagramService())

    registry.run(*sys.argv[1:])


if __name__ == "__main__":
    main()
