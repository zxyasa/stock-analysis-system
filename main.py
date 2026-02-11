"""Compatibility entrypoint. Prefer src.app.run for new integrations."""

from src.app import run


if __name__ == "__main__":
    run()
