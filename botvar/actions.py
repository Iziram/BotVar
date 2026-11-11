"""Logique des commandes, indépendante de Discord.

Chaque fonction représente une « action » (legend, player, teams, help) et
retourne une structure de résultat simple (dictionnaire). L'affichage et le
transport (Discord, terminal) sont gérés par le bot, le REPL ou le CLI, qui
interprètent ce résultat. Cela permet de partager exactement la même logique
entre les trois interfaces.
"""
from typing import Optional

from . import api
from .player import Player, statistics_formatter
from .team import Team

_OK = "success"
_ERR = "error"


def _get_player(id_discord: str) -> Player:
    player = Player.get(id_discord)
    if player is None:
        player = Player(id_discord)
    return player


def legend_rdm(id_discord: str) -> dict:
    """Tire aléatoirement une legend pour le joueur."""
    player = _get_player(id_discord)
    legend = player.random()
    return {"status": _OK, "legend": legend}


def legend_list(id_discord: str) -> dict:
    """Retourne les legends restantes du joueur."""
    player = _get_player(id_discord)
    return {
        "status": _OK,
        "legends": player.rest(),
        "count": len(player.legends),
    }


def legend_weapon() -> dict:
    """Retourne un challenge d'armes aléatoire."""
    return {"status": _OK, "weapon": Player.weapon()}


def player_steam(id_discord: str, steam_id: str) -> dict:
    """Lie l'id steam fourni au joueur."""
    player = _get_player(id_discord)
    player.set_steam_id(steam_id)
    if player.is_connected():
        return {"status": _OK, "message": "Votre compte steam a bien été relié."}
    return {
        "status": _ERR,
        "message": "Votre compte steam n'a pas pu être relié.",
    }


def _stats_result(player: Player, data, filename: str) -> dict:
    return {"status": _OK, "data": data, "filename": filename}


def player_stats(id_discord: str) -> dict:
    """Retourne les statistiques du joueur (formattées)."""
    player = _get_player(id_discord)
    if player is None or not player.is_connected():
        return {
            "status": _ERR,
            "message": "Votre compte steam n'a pas été relié, vous ne pouvez pas"
            " accédez à vos données brawlhalla",
        }
    data = statistics_formatter(api.get_player_stats(player.brawlhalla_id))
    return _stats_result(player, data, "stats.json")


def player_ranked(id_discord: str) -> dict:
    """Retourne les statistiques ranked du joueur (formattées)."""
    player = _get_player(id_discord)
    if player is None or not player.is_connected():
        return {
            "status": _ERR,
            "message": "Votre compte steam n'a pas été relié, vous ne pouvez pas"
            " accédez à vos données brawlhalla",
        }
    data = statistics_formatter(
        api.get_player_ranked(player.brawlhalla_id), "ranked"
    )
    return _stats_result(player, data, "ranked.json")


def player_clan(id_discord: str) -> dict:
    """Retourne les informations du clan du joueur."""
    player = _get_player(id_discord)
    if player is None or not player.is_connected():
        return {
            "status": _ERR,
            "message": "Votre compte steam n'a pas été relié, vous ne pouvez pas"
            " accédez à vos données brawlhalla",
        }
    stats = api.get_player_stats(player.brawlhalla_id)
    if stats is None or "clan" not in stats.keys():
        return {"status": _ERR, "message": "Vous n'avez pas de clan."}
    data = api.get_clan(stats["clan"]["clan_id"])
    return _stats_result(player, data, "clan.json")


def teams_new(room_code: Optional[str] = None) -> dict:
    """Lance une nouvelle partie (retourne le texte de l'annonce)."""
    code = ""
    if room_code:
        code = f"RoomCode : {room_code}"
    return {"status": _OK, "text": f"Une nouvelle partie a été lancée. {code}"}


def teams_list() -> dict:
    """Retourne les participants en attente."""
    return {"status": _OK, "participants": list(Team.participants())}


def teams_select() -> dict:
    """Répartit les joueurs en attente dans les équipes rouge et bleue."""
    Team.selection()
    return {
        "status": _OK,
        "red": list(Team.teamRed.players),
        "blue": list(Team.teamBlue.players),
    }


def teams_reset() -> dict:
    """Réinitialise la partie en cours."""
    Team.init()
    return {"status": _OK, "text": "La partie a été réinitialisée."}


HELP_GENERAL = """
!b help ➡ affiche la liste des commandes
!b legend ➡ commandes relatives aux legendes
!b player ➡ commandes relatives aux joueurs
!b teams ➡ commandes relatives aux parties

Pour plus d'informations sur une commande :
!b help <commande>
"""

HELP_LEGEND = """
!b legend list ➡ Affiche la liste des legendes que vous n'avez pas encore utilisé
!b legend rdm ➡ Tire aléatoirement une legende
!b legend weapon ➡ Tire aléatoirement un challenge d'armes (restriction des armes à utiliser)
"""

HELP_PLAYER = """
!b player steam <steam_id> ➡ Lie votre compte discord à votre compte steam
!b player stats ➡ Affiche vos statistiques brawhalla
!b player ranked ➡ Affiche vos statistiques ranked brawlhalla
!b player clan ➡ Affiche des informations sur votre clan brawlhalla
"""

HELP_TEAMS = """
*Seuls les membres ayant le role JiroBot pourront utiliser ces commandes*

!b teams new [Roomcode] ➡ génère une nouvelle partie brawlhalla le roomcode n'est pas obligatoire
!b teams list ➡ Affiche la liste des participants à la partie
!b teams select ➡ Selectionne les équipes aléatoirement
!b teams reset ➡ Réinitialise la partie
"""


def help(topic: Optional[str] = None) -> dict:
    """Retourne le texte d'aide général ou d'une catégorie."""
    if topic is None:
        return {"status": _OK, "text": HELP_GENERAL.strip()}
    topic = topic.lower()
    if topic == "legend":
        return {"status": _OK, "text": HELP_LEGEND.strip()}
    if topic == "player":
        return {"status": _OK, "text": HELP_PLAYER.strip()}
    if topic == "teams":
        return {"status": _OK, "text": HELP_TEAMS.strip()}
    return {
        "status": _ERR,
        "message": f"La catégorie '{topic}' n'existe pas. Faites !b help pour"
        " avoir la liste des commandes",
    }


def handle_command(tokens: list, id_discord: str) -> dict:
    """Interprète une commande sous forme de liste de tokens.

    ``tokens`` doit être déjà en minuscules et commencer par ``!b`` suivi de la
    commande, ex. : ``["!b", "legend", "rdm"]``.

    :param tokens: tokens de la commande.
    :param id_discord: id discord de l'auteur.
    :return: dictionnaire de résultat interprétable par n'importe quelle interface.
    """
    if len(tokens) < 2 or tokens[0] != "!b":
        return {"status": _ERR, "message": "Commande vide. Utilisez !b help."}

    command = tokens[1]
    args = tokens[2:]

    if command == "legend":
        if args and args[0] == "rdm":
            return legend_rdm(id_discord)
        if args and args[0] == "list":
            return legend_list(id_discord)
        if args and args[0] == "weapon":
            return legend_weapon()
        return {"status": _ERR, "message": "Utilisez !b help legend."}

    if command == "player":
        if len(args) >= 2 and args[0] == "steam":
            return player_steam(id_discord, args[1])
        if args and args[0] == "stats":
            return player_stats(id_discord)
        if args and args[0] == "ranked":
            return player_ranked(id_discord)
        if args and args[0] == "clan":
            return player_clan(id_discord)
        return {"status": _ERR, "message": "Utilisez !b help player."}

    if command == "teams":
        if args and args[0] == "new":
            return teams_new(args[1] if len(args) > 1 else None)
        if args and args[0] == "list":
            return teams_list()
        if args and args[0] == "select":
            return teams_select()
        if args and args[0] == "reset":
            return teams_reset()
        return {"status": _ERR, "message": "Utilisez !b help teams."}

    if command == "help":
        return help(args[0] if args else None)

    return {
        "status": _ERR,
        "message": f"La commande '{command}' n'existe pas. Faites !b help pour"
        " avoir la liste des commandes",
    }
