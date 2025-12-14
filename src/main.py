import sys
import asyncio

from .backend import BackEnd
from .init import Init


def main() -> None:
    args = sys.argv[1:]

    for arg in args:
        match arg:
            case "backend":
                backend = BackEnd()
                backend.start()
            case "gtfs-feed":
                init = Init()
                asyncio.run(init.load_gtfs_rt())
            case "frontend":
                print("frontend starting")
            case _:
                raise Exception


if __name__ == "__main__":
    main()
