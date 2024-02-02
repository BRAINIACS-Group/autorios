

#STL imports
import logging

#local imports
from .cli import cli

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()