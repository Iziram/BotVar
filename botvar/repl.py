"""! @brief Mode REPL : les commandes du bot sans passer par discord
 @file repl.py

 Permet de tester la logique (legends, joueur, teams) en local, sans
 compte discord. La clé d'api Brawlhalla est lue depuis la variable
 d'environnement ``BRAWLHALLA_API_KEY`` ou le fichier ``apikey.txt``.
"""
from .api import BrawlhallaAPI
from .player import Player
from .teams import Team


class Repl:
    """REPL simple qui exécute les mêmes commandes que le bot discord."""

    BANNER = """BotVar REPL — tapez 'help' pour la liste des commandes, 'quit' pour sortir."""

    def __init__(self, user_id: str = "repl", api_key: str = ""):
        self.user_id = user_id
        if api_key:
            BrawlhallaAPI.api_key = api_key
        Player.reset()
        Team.init()

    def _player(self) -> Player:
        player = Player.get(self.user_id)
        if player is None:
            player = Player(self.user_id)
        return player

    def _handle(self, line: str) -> str:
        """Interprète une ligne de commande et renvoie le texte à afficher."""
        parts = [p.lower() for p in line.split()]
        if not parts or parts[0] in ("quit", "exit", "q"):
            return "Au revoir !"
        if parts[0] in ("help", "?"):
            return self._help()
        command = parts[0]
        if command == "legend":
            return self._legend(parts)
        if command == "player":
            return self._player_cmd(parts)
        if command == "teams":
            return self._teams(parts)
        return f"Commande inconnue : {command}. Tapez 'help'."

    def _help(self) -> str:
        return """Commandes disponibles :
  legend rdm | list | weapon   - tirage de legend / challenge d'armes
  player steam <steam_id>      - lier son compte steam
  player stats | ranked | clan - statistiques brawlhalla
  teams new [roomcode] | list | select | reset
  quit                         - quitter le REPL
"""

    def _legend(self, parts: list) -> str:
        if len(parts) < 2:
            return "Usage : legend rdm | list | weapon"
        sub = parts[1]
        player = self._player()
        if sub == "rdm":
            return f"Utilise : {player.random()}"
        if sub == "list":
            return (
                f"Legends restantes ({len(player.legends)}):\n"
                f"{player.rest()}"
            )
        if sub == "weapon":
            return f"Arme(s) à utiliser : {Player.weapon()}"
        return f"Option inconnue : {sub}"

    def _player_cmd(self, parts: list) -> str:
        if len(parts) < 2:
            return "Usage : player steam <steam_id> | stats | ranked | clan"
        sub = parts[1]
        player = self._player()
        if sub == "steam":
            if len(parts) < 3:
                return "Usage : player steam <steam_id>"
            player.set_steam_id(parts[2])
            if player.is_connected():
                return "Votre compte steam a bien été relié."
            return "Votre compte steam n'a pas pu être relié."
        if player.is_connected() is False:
            return "Votre compte steam n'a pas été relié, vous ne pouvez pas " \
                   "accédez à vos données brawlhalla"
        if sub == "stats":
            stats = BrawlhallaAPI.get_player_stats(player.brawlhalla_id)
            if stats is None:
                return "Impossible de récupérer vos statistiques."
            return self._stats_text(stats, "stat")
        if sub == "ranked":
            stats = BrawlhallaAPI.get_player_ranked(player.brawlhalla_id)
            if stats is None:
                return "Impossible de récupérer vos statistiques ranked."
            return self._stats_text(stats, "ranked")
        if sub == "clan":
            stats = BrawlhallaAPI.get_player_stats(player.brawlhalla_id)
            if stats is not None and "clan" in stats:
                clan = BrawlhallaAPI.get_clan(stats["clan"]["clan_id"])
                return f"Clan : {clan}"
            return "Vous n'avez pas de clan."
        return f"Option inconnue : {sub}"

    @staticmethod
    def _stats_text(stats: dict, kind: str) -> str:
        from .stats import format as format_stats

        data = format_stats(stats, kind)
        p = data["player"]
        lines = []
        if kind == "ranked":
            lines.append(
                f"{p['name']} — rating {p['rating']['current']} "
                f"(pic {p['rating']['peak']}, {p['rating']['tier']})"
            )
        else:
            lines.append(f"{p['name']} — niveau {p['level']}")
        lines.append(
            f"Parties : {p['games']['total']} (victoires : {p['games']['wins']})"
        )
        for legend in data["legends"]:
            if kind == "ranked":
                lines.append(
                    f"  {legend['name']}: {legend['rating']['current']} "
                    f"({legend['rating']['tier']}), {legend['games']['wins']}/"
                    f"{legend['games']['total']}"
                )
            else:
                lines.append(
                    f"  {legend['name']}: {legend['kos']} kos, "
                    f"{legend['games']['wins']}/{legend['games']['total']} parties"
                )
        return "\n".join(lines)

    def _teams(self, parts: list) -> str:
        if len(parts) < 2:
            return "Usage : teams new [roomcode] | list | select | reset"
        sub = parts[1]
        if sub == "new":
            Team.init()
            code = (" RoomCode : " + parts[2]) if len(parts) > 2 else ""
            return f"Une nouvelle partie a été lancée.{code}"
        if sub == "list":
            if not Team.participants():
                return "Aucun participant."
            return "Participants : " + ", ".join(map(str, Team.participants()))
        if sub == "select":
            red, blue = Team.select()
            return f"Rouges : {red}\nBleus : {blue}"
        if sub == "reset":
            Team.init()
            return "La partie a été réinitialisée."
        return f"Option inconnue : {sub}"

    def run(self) -> None:
        """Boucle REPL interactive (lecture au clavier)."""
        print(self.BANNER)
        while True:
            try:
                line = input("botvar> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            result = self._handle(line)
            if "Au revoir" in result:
                break
            print(result)
