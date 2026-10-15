"""Allows `python -m sitepulse check https://example.com`."""

import sys

from sitepulse.cli import main

if __name__ == "__main__":
    sys.exit(main())
