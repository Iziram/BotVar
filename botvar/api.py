"""Interface vers l'API publique BrawlHalla.

Toutes les requêtes HTTP vers https://api.brawlhalla.com sont centralisées ici.
La clé d'API est fournie une seule fois via :func:`set_api_key`.
"""
from typing import Optional

import requests

API_BASE = "https://api.brawlhalla.com"

_api_key: str = ""


def set_api_key(api_key: str) -> None:
    """Définit la clé d'API BrawlHalla utilisée par toutes les requêtes."""
    global _api_key
    _api_key = api_key


def get_api_key() -> str:
    """Retourne la clé d'API courante (utile pour les tests)."""
    return _api_key


def get_brawlhalla_id_from_steam_id(steam_id: str) -> Optional[int]:
    """Obtient le brawlhalla id d'un joueur à partir de son steam id.

    :param steam_id: identifiant steam (paramètres du compte steam).
    :return: le brawlhalla id, ou ``None`` si la requête échoue.
    """
    reponse = requests.get(
        f"{API_BASE}/search?steamid={steam_id}&api_key={_api_key}"
    )
    if reponse.status_code == 200:
        return reponse.json().get("brawlhalla_id", None)
    return None


def get_player_stats(brawlhalla_id: int) -> Optional[dict]:
    """Récupère les statistiques d'un joueur à partir de son brawlhalla id."""
    reponse = requests.get(
        f"{API_BASE}/player/{brawlhalla_id}/stats?&api_key={_api_key}"
    )
    if reponse.status_code == 200:
        return reponse.json()
    return None


def get_player_ranked(brawlhalla_id: int) -> Optional[dict]:
    """Récupère les statistiques ranked d'un joueur à partir de son brawlhalla id."""
    reponse = requests.get(
        f"{API_BASE}/player/{brawlhalla_id}/ranked?&api_key={_api_key}"
    )
    if reponse.status_code == 200:
        return reponse.json()
    return None


def get_all_legends() -> Optional[list]:
    """Obtient la liste de toutes les legends du jeu (liste de noms)."""
    reponse = requests.get(f"{API_BASE}/legend/all/&api_key={_api_key}")
    if reponse.status_code == 200:
        json = reponse.json()
        return [legend["legend_name_key"] for legend in json]
    return None


def get_legends_of_player(brawlhalla_id: str) -> Optional[list]:
    """Obtient la liste des legends qu'un joueur possède."""
    stats = get_player_stats(brawlhalla_id)
    if stats is None:
        return None
    return [l["legend_name_key"] for l in stats["legends"]]


def get_clan(clan_id: str) -> Optional[dict]:
    """Obtient les informations d'un clan à partir de son id."""
    reponse = requests.get(f"{API_BASE}/clan/{clan_id}/?&api_key={_api_key}")
    if reponse.status_code == 200:
        return reponse.json()
    return None
