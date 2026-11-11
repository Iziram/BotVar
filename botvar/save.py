"""! @brief Sauvegarde des joueurs sur le disque
 @file save.py

 Le format est une liste de json, un par joueur (compatible avec l'ancienne
 sauvegarde ``save.json``).
"""
import json
from pathlib import Path


def save(players: dict, path: str | Path = "save.json") -> None:
    """!
    @brief Écris la liste des joueurs dans le fichier de sauvegarde.

    @param players : dict => dictionnaire id discord -> objet Player
    @param path : str => chemin du fichier de sauvegarde
    """
    path = Path(path)
    if path.exists():
        path.unlink()
    with open(path, "w", encoding="utf-8") as f:
        json.dump([p.to_json() for p in players.values()], f)


def load(path: str | Path = "save.json") -> list:
    """!
    @brief Charge la liste des joueurs depuis le fichier de sauvegarde.

    @param path : str => chemin du fichier de sauvegarde
    @return list => liste des dicts joueurs (vide si le fichier n'existe pas)
    """
    path = Path(path)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)
