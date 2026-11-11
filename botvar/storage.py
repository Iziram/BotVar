"""Persistance des joueurs sur disque (fichier JSON)."""
import json
import os
from typing import Optional


def load_save(path: str = "./save.json") -> Optional[list]:
    """Charge la liste des joueurs sauvegardés.

    :param path: chemin du fichier de sauvegarde.
    :return: la liste des joueurs (list de dict), ou ``None`` si absent.
    """
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def save_players(players, path: str = "./save.json") -> None:
    """Écrit la liste des joueurs dans le fichier de sauvegarde.

    :param players: itérables d'objets :class:`botvar.player.Player`.
    :param path: chemin du fichier de sauvegarde.
    """
    if os.path.exists(path):
        os.remove(path)
    with open(path, "w") as f:
        json.dump([p.to_json() for p in players], f)
