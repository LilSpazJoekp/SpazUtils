"""SpazUtils: Utilities for Automating Moderation on Reddit."""

from .flairRemoval import FlairRemoval
from .usernotes import Usernotes
from .info import __version__
import logging

logging.getLogger(__package__).addHandler(logging.NullHandler())