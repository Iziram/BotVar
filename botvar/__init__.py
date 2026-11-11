"""BotVar : bot Discord pour le serveur communautaire BrawlHalla.

Le package est découpé en modules spécialisés :

- :mod:`botvar.api` : requêtes vers l'API BrawlHalla.
- :mod:`botvar.player` : modèle joueur et formatage de statistiques.
- :mod:`botvar.team` : gestion des équipes d'une partie.
- :mod:`botvar.storage` : persistance des joueurs (``save.json``).
- :mod:`botvar.actions` : logique des commandes (indépendante de Discord),
  réutilisée par le bot Discord, le REPL et le CLI.
- :mod:`botvar.discord_bot` : le bot Discord (interface).
- :mod:`botvar.repl` : mode interactif hors Discord.
- :mod:`botvar.cli` : interface en ligne de commande.
"""
from .player import Player, statistics_formatter
from .team import Team

__all__ = ["Player", "Team", "statistics_formatter"]
__version__ = "0.1.0"
