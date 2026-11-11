"""Gestion des équipes d'une partie (rouge, bleu, attente)."""
from random import shuffle


class Team:
    """Une équipe identifiée par sa couleur.

    ``color`` est l'un de : ``"red"``, ``"blue"`` ou ``"waiter"`` (attente).
    Les trois équipes globales d'une partie sont accessibles via les
    variables de classe :pyattr:`teamRed` / :pyattr:`teamBlue` / :pyattr:`teamWaiter`.
    """

    # Réaction utilisée par le bot pour rejoindre l'équipe d'attente.
    teamReaction = ""
    # Équipes globales d'une partie (variables statiques).
    teamRed = None
    teamBlue = None
    teamWaiter = None

    def __init__(self, color: str):
        self.color = color
        self.players = []

    def add(self, player) -> None:
        """Ajoute un joueur à l'équipe."""
        self.players.append(player)

    def remove(self, player) -> None:
        """Retire un joueur de l'équipe s'il y est présent."""
        if player in self.players:
            self.players.remove(player)

    def melange(self) -> None:
        """Mélange aléatoirement les joueurs de l'équipe."""
        shuffle(self.players)

    def __len__(self) -> int:
        return len(self.players)

    @staticmethod
    def participants() -> list:
        """Renvoie les joueurs en attente (ou une liste vide)."""
        if len(Team.teamWaiter) > 0:
            return Team.teamWaiter.players
        return []

    @staticmethod
    def init() -> None:
        """Crée les trois équipes (rouge, bleu, attente)."""
        Team.teamRed = Team("red")
        Team.teamBlue = Team("blue")
        Team.teamWaiter = Team("waiter")

    @staticmethod
    def selection() -> None:
        """Répartit aléatoirement les joueurs en attente entre rouge et bleu."""
        Team.teamWaiter.melange()
        players = Team.teamWaiter.players
        mid = len(players) // 2
        red = players[:mid]
        blue = players[mid:]
        Team.teamBlue.players = blue
        Team.teamRed.players = red
