"""Mode REPL : interagir avec BotVar sans passer par Discord.

Lancez ``botvar repl`` (ou :func:`main`) pour ouvrir un shell interactif qui
exécute les mêmes commandes que le bot.
"""
import sys

from . import actions, config, render


BANNER = """
BotVar REPL — commandes BrawlHalla sans Discord
Entrez une commande (ex. : !b legend rdm) ou 'help'.
'exit' / 'quit' pour quitter.
"""

PROMPT = "botvar> "


def _init_player() -> str:
    """Demande / mémorise l'identifiant du joueur en session.

    Retourne l'id utilisé pour la session (chaîne arbitraire ; id Discord en
    production, libellé libre ici).
    """
    default = "local"
    raw = input(f"Identifiant du joueur (défaut '{default}') : ").strip()
    return raw or default


def main() -> int:
    """Boucle principale du REPL."""
    print(BANNER)

    api_key = config.load_api_key()
    config.init_api(api_key)
    from .player import Player

    Player.load_from_save()

    player_id = _init_player()
    print(f"Session ouverte pour '{player_id}'.\n")

    while True:
        try:
            line = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            break

        tokens = line.lower().split(" ")
        if tokens[0] != "!b":
            result = {"status": "error", "message": "Commencez la commande par '!b'."}
        else:
            result = actions.handle_command(tokens, player_id)

        # Les résultats avec données sont aussi écrits dans un fichier JSON.
        if "data" in result:
            path = render.save_json(result)
            print(f"(données écrites dans {path})")

        print(render.render(result) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
