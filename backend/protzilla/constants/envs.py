import os

DEBUGMODE: bool = bool(int(os.getenv("DEBUGMODE", 0)))
