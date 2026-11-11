"""! @brief Interface en ligne de commande de BotVar
 @file cli.py

 Utilisation :
   botvar [--api-key KEY] [--user ID] <commande>

 Commandes :
   bot            lance le bot discord (nécessite DISCORD_TOKEN)
   repl           démarre le REPL interactif (sans discord)
   legend <opt>   rdm | list | weapon
   player <opt>   steam <id> | stats | ranked | clan
   teams <opt>    new [roomcode] | list | select | reset
   save           sauvegarde les joueurs connus
"""
import argparse
import json
import sys

import requests as _requests

from . import __version__
from .api import BrawlhallaAPI
from .discord_bot import load_tokens, run as run_bot
from .player import Player
from .repl import Repl
from .stats import format as format_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="botvar",
        description="BotVar : bot discord et CLI Brawlhalla.",
    )
    parser.add_argument("--version", action="version", version=f"botvar {__version__}")
    parser.add_argument("--api-key", default="", help="clé d'api Brawlhalla")
    parser.add_argument(
        "--user", default="repl", help="id utilisateur local (défaut : repl)"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("bot", help="lancer le bot discord")
    sub.add_parser("repl", help="lancer le REPL interactif")

    p_legend = sub.add_parser("legend", help="commandes legend")
    p_legend.add_argument("option", choices=["rdm", "list", "weapon"])

    p_player = sub.add_parser("player", help="commandes joueur")
    p_player.add_argument("option", choices=["steam", "stats", "ranked", "clan"])
    p_player.add_argument("steam_id", nargs="?", default="")

    p_teams = sub.add_parser("teams", help="commandes équipes")
    p_teams.add_argument("option", choices=["new", "list", "select", "reset"])
    p_teams.add_argument("roomcode", nargs="?", default="")

    sub.add_parser("save", help="sauvegarder les joueurs")
    return parser


def _init(args) -> None:
    api_key = args.api_key
    if not api_key:
        api_key, _ = load_tokens()
    if api_key:
        BrawlhallaAPI.api_key = api_key
    Player.reset()
    try:
        legends = BrawlhallaAPI.get_all_legends()
    except _requests.exceptions.RequestException:
        legends = None
    if legends:
        Player.legends = legends


def _print_stats(stats: dict, kind: str) -> None:
    print(json.dumps(format_stats(stats, kind), indent=2, ensure_ascii=False))


def _dispatch(args) -> int:
    if args.command is None:
        build_parser().print_help()
        return 0

    if args.command == "bot":
        run_bot()
        return 0

    if args.command == "repl":
        Repl(user_id=args.user, api_key=args.api_key).run()
        return 0

    _init(args)
    repl = Repl(user_id=args.user, api_key=args.api_key)

    if args.command == "legend":
        print(repl._legend(["legend", args.option]))
    elif args.command == "player":
        if args.option == "steam":
            if not args.steam_id:
                print("Usage : botvar player steam <steam_id>", file=sys.stderr)
                return 2
            print(repl._player_cmd(["player", "steam", args.steam_id]))
        else:
            print(repl._player_cmd(["player", args.option]))
    elif args.command == "teams":
        parts = ["teams", args.option]
        if args.option == "new" and args.roomcode:
            parts.append(args.roomcode)
        print(repl._teams(parts))
    elif args.command == "save":
        Player.save_all()
        print("Sauvegarde effectuée : save.json")
    return 0


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return _dispatch(args)


if __name__ == "__main__":
    raise SystemExit(main())
