#!/usr/bin/env python3
"""
This file is deprecated, __main__.py is the replacement to allow `python -mapplitools` invokation.
Required to run from zip file
"""

import sys
from src.instrument import run

# stop writ *.pyc files to prevent from caching
sys.dont_write_bytecode = True

__version__ = "0.1.0"

def main():
    run()

if __name__ == "__main__":
    if sys.version_info < (3, 7):
        raise SystemError("Minimum required Python version is 3.7")
    main()
