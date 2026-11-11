"""BotVar : bot Discord et CLI pour un serveur communautaire Brawlhalla."""

__version__ = "0.1.0"

from .api import BrawlhallaAPI, brawlhallaAPI
from .player import Player
from .teams import Team

__all__ = ["BrawlhallaAPI", "brawlhallaAPI", "Player", "Team", "__version__"]
