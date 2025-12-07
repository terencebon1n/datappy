import sys

from .backend import BackEnd


def main() -> None:
    args = sys.argv[1:]

    for arg in args:
        match arg:
            case "backend":
                backend = BackEnd()
                backend.start()
            case "frontend":
                print("frontend starting")
            case _:
                raise Exception


if __name__ == "__main__":
    main()
