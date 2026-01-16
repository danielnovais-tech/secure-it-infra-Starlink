#!/usr/bin/env python3
"""Development entry point.

For packaged usage, prefer the console script:

  starlink-security --config /path/to/config.yaml

This file is kept as a thin wrapper for local development.
"""

from starlink_security.foundation import main


if __name__ == "__main__":
    main()