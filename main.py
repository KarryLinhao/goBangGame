import sys

try:
    from gobang.app import run
except ModuleNotFoundError as exc:
    if exc.name == "pygame":
        print("Missing dependency: pygame")
        print("Install it with: python3 -m pip install -r requirements.txt")
        sys.exit(1)
    raise


if __name__ == "__main__":
    run()
