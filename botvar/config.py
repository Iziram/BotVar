"""Chargement de la configuration (clés d'API, token).

Les secrets sont lus depuis le fichier ``apikey.txt`` (gitignored) :
``<clé_api_brawlhalla> <token_discord>``. La clé d'API est aussi disponible via
la variable d'environnement ``BRAWLHALLA_API_KEY``.
"""
import os
from typing import Optional


def load_api_key(path: str = "./apikey.txt") -> Optional[str]:
    """Cherche la clé d'API BrawlHalla (variable d'env puis fichier)."""
    env_key = os.environ.get("BRAWLHALLA_API_KEY")
    if env_key:
        return env_key
    if os.path.exists(path):
        with open(path) as f:
            tokens = f.readline().split(" ")
            if tokens and tokens[0]:
                return tokens[0]
    return None


def load_discord_token(path: str = "./apikey.txt") -> Optional[str]:
    """Cherche le token Discord (variable d'env puis fichier)."""
    env_token = os.environ.get("DISCORD_TOKEN")
    if env_token:
        return env_token
    if os.path.exists(path):
        with open(path) as f:
            tokens = f.readline().split(" ")
            if len(tokens) > 1 and tokens[1]:
                return tokens[1]
    return None


def init_api(api_key: Optional[str]) -> bool:
    """Configure l'API et la liste des legends si une clé est disponible.

    :return: ``True`` si une clé a été configurée.
    """
    from . import api
    from .player import Player

    if api_key:
        api.set_api_key(api_key)
        legends = api.get_all_legends()
        if legends:
            Player.legends = legends
        return True
    return False
