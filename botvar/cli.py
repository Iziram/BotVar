"""Interface en ligne de commande (CLI) de BotVar.

Exemples :
    botvar legend rdm
    botvar player steam 123456789
    botvar player stats --save
    botvar teams new 1234
    botvar repl
"""
import argparse
import sys

from . import actions, config, render


def _add_player_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--player",
        default="local",
        help="identifiant du joueur (défaut : local)",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="botvar",
        description="BotVar : commandes BrawlHalla (Discord, REPL ou CLI).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # legend
    p = sub.add_parser("legend", help="commandes relatives aux legends")
    p.add_argument(
        "mode", choices=["rdm", "list", "weapon"], help="type de tirage"
    )
    _add_player_args(p)

    # player
    p = sub.add_parser("player", help="commandes relatives au joueur")
    p.add_argument(
        "mode",
        choices=["steam", "stats", "ranked", "clan"],
        help="type de commande",
    )
    p.add_argument("steam_id", nargs="?", help="id steam (pour le mode steam)")
    _add_player_args(p)
    p.add_argument("--save", action="store_true", help="écrit le résultat dans un fichier JSON")

    # teams
    p = sub.add_parser("teams", help="commandes relatives aux parties")
    p.add_argument(
        "mode", choices=["new", "list", "select", "reset"], help="type de commande"
    )
    p.add_argument("room_code", nargs="?", help="room code (pour le mode new)")

    # help
    p = sub.add_parser("help", help="affiche l'aide")
    p.add_argument("topic", nargs="?", help="catégorie (legend, player, teams)")

    # repl
    sub.add_parser("repl", help="ouvre le mode interactif")

    return parser


def _run(args: argparse.Namespace) -> int:
    config.init_api(config.load_api_key())
    from .player import Player

    Player.load_from_save()

    if args.command == "repl":
        from . import repl

        return repl.main()

    if args.command == "legend":
        if args.mode == "rdm":
            result = actions.legend_rdm(args.player)
        elif args.mode == "list":
            result = actions.legend_list(args.player)
        else:
            result = actions.legend_weapon()
    elif args.command == "player":
        if args.mode == "steam":
            if not args.steam_id:
                print("Erreur : un id steam est requis.", file=sys.stderr)
                return 1
            result = actions.player_steam(args.player, args.steam_id)
        elif args.mode == "stats":
            result = actions.player_stats(args.player)
        elif args.mode == "ranked":
            result = actions.player_ranked(args.player)
        else:
            result = actions.player_clan(args.player)
        if args.save and "data" in result:
            path = render.save_json(result)
            print(f"(données écrites dans {path})")
    elif args.command == "teams":
        if args.mode == "new":
            result = actions.teams_new(args.room_code)
        elif args.mode == "list":
            result = actions.teams_list()
        elif args.mode == "select":
            result = actions.teams_select()
        else:
            result = actions.teams_reset()
    elif args.command == "help":
        result = actions.help(args.topic)
    else:  # pragma: no cover
        return 1

    print(render.render(result))
    return 0 if result.get("status") == "success" else 1


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return _run(args)


if __name__ == "__main__":
    sys.exit(main())
