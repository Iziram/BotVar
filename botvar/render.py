"""Affichage terminal des résultats d'action (REPL et CLI).

Chaque fonction transforme le dictionnaire de résultat retourné par
:mod:`botvar.actions` en texte lisible pour le terminal.
"""
import json
from typing import Optional

from . import api


def render(result: dict) -> str:
    """Transforme un résultat d'action en texte terminal."""
    status = result.get("status")
    if status == "error":
        return f"[erreur] {result.get('message', '')}"

    if "text" in result:
        return result["text"]

    if "legend" in result:
        return f"Utilise : {result['legend']}"

    if "weapon" in result:
        return f"Arme(s) à utiliser : {result['weapon']}"

    if "legends" in result:
        return (
            "Tu n'as pas encore utilisé les legendes suivantes :"
            f" {result['legends']} ({result['count']})"
        )

    if "participants" in result:
        names = [getattr(p, "name", str(p)) for p in result["participants"]]
        if not names:
            return "Aucun participant."
        return "\n".join(f"- {n}" for n in names)

    if "red" in result and "blue" in result:
        red = [getattr(p, "name", str(p)) for p in result["red"]]
        blue = [getattr(p, "name", str(p)) for p in result["blue"]]
        return (
            "Les Rouges sont : "
            + (", ".join(red) or "-")
            + "\nLes Bleus sont : "
            + (", ".join(blue) or "-")
        )

    if "data" in result:
        return json.dumps(result["data"], indent=2, ensure_ascii=False)

    if "message" in result:
        return result["message"]

    return json.dumps(result, indent=2, ensure_ascii=False)


def save_json(result: dict, path: Optional[str] = None) -> Optional[str]:
    """Écrit le ``data`` d'un résultat dans un fichier JSON.

    :return: le chemin écrit, ou ``None`` s'il n'y a pas de ``data``.
    """
    if "data" not in result:
        return None
    filename = path or result.get("filename", "output.json")
    with open(filename, "w") as f:
        json.dump(result["data"], f, indent=2, ensure_ascii=False)
    return filename
