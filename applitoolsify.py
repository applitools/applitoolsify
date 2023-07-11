#!/usr/bin/env python3
import sys
from urllib.request import urlretrieve
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
