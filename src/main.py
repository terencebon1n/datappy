import asyncio
import sys

from src import Init
from src.backend import BackEnd


def main() -> None:
    args = sys.argv[1:]

    for arg in args:
        match arg:
            case "backend":
                backend = BackEnd()
                backend.start()
            case "producer":
                init = Init()
                asyncio.run(init.gtfs_rt_producer())
            case "consumer":
                init = Init()
                init.gtfs_rt_consumer()
            case "frontend":
                print("frontend starting")
            case _:
                raise Exception


if __name__ == "__main__":
    main()
