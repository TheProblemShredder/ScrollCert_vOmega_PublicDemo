#!/usr/bin/env python3
"""
Root entrypoint with arg forwarding.
Usage:
  ./run.py
  ./run.py --blind --salt "my_salt"
  python3 -m src.run --blind --salt "my_salt"
"""
from src.run import main

if __name__ == "__main__":
    main()
